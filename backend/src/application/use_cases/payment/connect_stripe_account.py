"""
Connect Stripe Account Use Case

Caso de uso para onboarding do instrutor no Stripe Connect.
"""

from dataclasses import dataclass

from src.application.dtos.payment_dtos import (
    ConnectStripeAccountDTO,
    StripeConnectResponseDTO,
)
from src.domain.entities.user_type import UserType
from src.domain.exceptions import (
    InstructorNotFoundException,
    UserNotFoundException,
)
from src.domain.interfaces.instructor_repository import IInstructorRepository
from src.domain.interfaces.payment_gateway import IPaymentGateway
from src.domain.interfaces.user_repository import IUserRepository


@dataclass
class ConnectStripeAccountUseCase:
    """
    Caso de uso para conectar instrutor ao Stripe Connect.

    Fluxo:
        1. Validar que usuário é instrutor
        2. Verificar se já possui conta Stripe
        3. Chamar IPaymentGateway.create_connected_account
        4. Salvar stripe_account_id no perfil do instrutor
        5. Gerar link de onboarding
        6. Retornar StripeConnectResponseDTO com URL
    """

    user_repository: IUserRepository
    instructor_repository: IInstructorRepository
    payment_gateway: IPaymentGateway

    async def execute(self, dto: ConnectStripeAccountDTO) -> StripeConnectResponseDTO:
        """
        Executa o processo de conexão com Stripe.

        Args:
            dto: Dados para conexão.

        Returns:
            StripeConnectResponseDTO: Resultado com URL de onboarding.

        Raises:
            UserNotFoundException: Se usuário não existir.
            InstructorNotFoundException: Se não for instrutor ou sem perfil.
        """
        # 1. Validar que usuário existe e é instrutor
        user = await self.user_repository.get_by_id(dto.instructor_id)
        if user is None:
            raise UserNotFoundException(str(dto.instructor_id))

        if user.user_type != UserType.INSTRUCTOR:
            raise InstructorNotFoundException(
                f"Usuário {dto.instructor_id} não é um instrutor"
            )

        # 2. Buscar perfil do instrutor
        instructor_profile = await self.instructor_repository.get_by_user_id(
            dto.instructor_id
        )
        if instructor_profile is None:
            raise InstructorNotFoundException(str(dto.instructor_id))

        # 3. Verificar se já possui conta Stripe
        if instructor_profile.stripe_account_id:
            # Já tem conta, gerar novo link de onboarding
            onboarding_url = await self.payment_gateway.create_account_link(
                account_id=instructor_profile.stripe_account_id,
                refresh_url=dto.refresh_url,
                return_url=dto.return_url,
            )

            # Verificar status da conta
            account_status = await self.payment_gateway.get_account_status(
                instructor_profile.stripe_account_id
            )

            return StripeConnectResponseDTO(
                account_id=instructor_profile.stripe_account_id,
                onboarding_url=onboarding_url,
                is_connected=account_status.get("charges_enabled", False),
            )

        # 4. Criar nova conta conectada
        account_result = await self.payment_gateway.create_connected_account(
            email=dto.email,
            instructor_id=dto.instructor_id,
        )

        # 5. Salvar stripe_account_id no perfil
        instructor_profile.stripe_account_id = account_result.account_id
        await self.instructor_repository.update(instructor_profile)

        # 6. Gerar link de onboarding
        onboarding_url = await self.payment_gateway.create_account_link(
            account_id=account_result.account_id,
            refresh_url=dto.refresh_url,
            return_url=dto.return_url,
        )

        return StripeConnectResponseDTO(
            account_id=account_result.account_id,
            onboarding_url=onboarding_url,
            is_connected=False,
        )
