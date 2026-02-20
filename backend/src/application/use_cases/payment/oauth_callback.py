"""
OAuthCallback Use Case

Processa o callback OAuth do Mercado Pago, trocando o code por tokens
e salvando no perfil do instrutor.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

import structlog

from src.application.dtos.payment_dtos import (
    OAuthCallbackDTO,
    OAuthCallbackResponseDTO,
)
from src.domain.exceptions import InstructorNotFoundException
from src.domain.interfaces.instructor_repository import IInstructorRepository
from src.domain.interfaces.payment_gateway import IPaymentGateway
from src.infrastructure.config import Settings
from src.infrastructure.services.token_encryption import encrypt_token

logger = structlog.get_logger()


class OAuthCallbackUseCase:
    """Processa callback OAuth e salva tokens do instrutor."""

    def __init__(
        self,
        instructor_repository: IInstructorRepository,
        payment_gateway: IPaymentGateway,
        settings: Settings,
    ) -> None:
        self.instructor_repository = instructor_repository
        self.payment_gateway = payment_gateway
        self.settings = settings

    async def execute(self, dto: OAuthCallbackDTO) -> OAuthCallbackResponseDTO:
        """
        Troca authorization code por tokens e salva no perfil do instrutor.

        Args:
            dto: OAuthCallbackDTO com code e state (instructor_user_id).

        Returns:
            OAuthCallbackResponseDTO com mp_user_id e status de conexão.

        Raises:
            InstructorNotFoundException: Se o instrutor do state não existir.
            ValueError: Se o instrutor já estiver conectado.
        """
        # 1. Extrair instructor_id do state
        try:
            instructor_user_id = UUID(dto.state)
        except ValueError:
            raise ValueError(f"State inválido no callback OAuth: {dto.state}")

        # 2. Buscar instrutor
        instructor = await self.instructor_repository.get_by_user_id(
            instructor_user_id
        )
        if instructor is None:
            raise InstructorNotFoundException(instructor_user_id)

        # 3. Verificar se já está conectado
        if instructor.has_mp_account:
            raise ValueError(
                f"Instrutor {instructor_user_id} já possui conta Mercado Pago vinculada"
            )

        # 4. Trocar code por tokens via gateway
        oauth_result = await self.payment_gateway.authorize_seller(
            authorization_code=dto.code,
            redirect_uri=self.settings.mp_redirect_uri,
        )

        # 5. Criptografar tokens antes de salvar
        encrypted_access_token = encrypt_token(oauth_result.access_token)
        encrypted_refresh_token = encrypt_token(oauth_result.refresh_token)

        # 6. Calcular data de expiração
        token_expiry = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(
            seconds=oauth_result.expires_in
        )

        # 7. Atualizar perfil do instrutor
        instructor.mp_access_token = encrypted_access_token
        instructor.mp_refresh_token = encrypted_refresh_token
        instructor.mp_token_expiry = token_expiry
        instructor.mp_user_id = oauth_result.user_id
        instructor.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

        await self.instructor_repository.update(instructor)

        logger.info(
            "instructor_mp_oauth_completed",
            instructor_user_id=str(instructor_user_id),
            mp_user_id=oauth_result.user_id,
        )

        return OAuthCallbackResponseDTO(
            mp_user_id=oauth_result.user_id,
            is_connected=True,
        )
