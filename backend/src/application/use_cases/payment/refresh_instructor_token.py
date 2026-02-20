"""
RefreshInstructorToken Use Case

Renova tokens OAuth expirados ou próximos de expirar dos instrutores.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

import structlog

from src.domain.exceptions import InstructorNotFoundException
from src.domain.interfaces.instructor_repository import IInstructorRepository
from src.domain.interfaces.payment_gateway import IPaymentGateway
from src.infrastructure.services.token_encryption import decrypt_token, encrypt_token

logger = structlog.get_logger()


class RefreshInstructorTokenUseCase:
    """Renova o access_token do instrutor via refresh_token."""

    # Renovar se expira em menos de 30 dias
    RENEWAL_THRESHOLD_DAYS = 30

    def __init__(
        self,
        instructor_repository: IInstructorRepository,
        payment_gateway: IPaymentGateway,
    ) -> None:
        self.instructor_repository = instructor_repository
        self.payment_gateway = payment_gateway

    async def execute(self, instructor_user_id: UUID) -> bool:
        """
        Renova os tokens OAuth do instrutor se estiverem próximos de expirar.

        Args:
            instructor_user_id: ID do usuário instrutor.

        Returns:
            True se os tokens foram renovados, False se não era necessário.

        Raises:
            InstructorNotFoundException: Se o instrutor não for encontrado.
            ValueError: Se o instrutor não tiver conta MP vinculada.
        """
        # 1. Buscar instrutor
        instructor = await self.instructor_repository.get_by_user_id(
            instructor_user_id
        )
        if instructor is None:
            raise InstructorNotFoundException(instructor_user_id)

        # 2. Verificar se tem conta MP
        if not instructor.has_mp_account:
            raise ValueError(
                f"Instrutor {instructor_user_id} não possui conta Mercado Pago vinculada"
            )

        # 3. Verificar se precisa renovar
        if instructor.mp_token_expiry is not None:
            threshold = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(
                days=self.RENEWAL_THRESHOLD_DAYS
            )
            if instructor.mp_token_expiry > threshold:
                logger.debug(
                    "token_renewal_not_needed",
                    instructor_user_id=str(instructor_user_id),
                    expiry=str(instructor.mp_token_expiry),
                )
                return False

        # 4. Descriptografar refresh_token atual
        decrypted_refresh_token = decrypt_token(instructor.mp_refresh_token)

        # 5. Chamar gateway para renovar
        oauth_result = await self.payment_gateway.refresh_seller_token(
            refresh_token=decrypted_refresh_token
        )

        # 6. Criptografar novos tokens
        encrypted_access_token = encrypt_token(oauth_result.access_token)
        encrypted_refresh_token = encrypt_token(oauth_result.refresh_token)

        # 7. Calcular nova data de expiração
        token_expiry = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(
            seconds=oauth_result.expires_in
        )

        # 8. Atualizar perfil
        instructor.mp_access_token = encrypted_access_token
        instructor.mp_refresh_token = encrypted_refresh_token
        instructor.mp_token_expiry = token_expiry
        instructor.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

        await self.instructor_repository.update(instructor)

        logger.info(
            "instructor_mp_token_refreshed",
            instructor_user_id=str(instructor_user_id),
            new_expiry=str(token_expiry),
        )

        return True
