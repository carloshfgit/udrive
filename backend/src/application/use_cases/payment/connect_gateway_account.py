"""
ConnectGatewayAccount Use Case
"""

from src.application.dtos.payment_dtos import (
    ConnectGatewayAccountDTO,
    GatewayConnectResponseDTO,
)
from src.domain.interfaces.instructor_repository import IInstructorRepository
from src.domain.interfaces.payment_gateway import IPaymentGateway


class ConnectGatewayAccountUseCase:
    """
    Caso de uso para conectar conta de pagamento de um instrutor.
    """

    def __init__(
        self,
        instructor_repository: IInstructorRepository,
        payment_gateway: IPaymentGateway,
    ) -> None:
        self.instructor_repository = instructor_repository
        self.payment_gateway = payment_gateway

    async def execute(self, dto: ConnectGatewayAccountDTO) -> GatewayConnectResponseDTO:
        """
        Inicia o processo de conexão de conta.
        
        Nota: Na Fase 4, este fluxo será implementado para o OAuth do Mercado Pago.
        Para a Fase 1, apenas garantimos compatibilidade com a interface agnóstica.
        """
        # 1. Buscar instrutor
        instructor_profile = await self.instructor_repository.get_by_user_id(
            dto.instructor_id
        )
        if instructor_profile is None:
            raise ValueError(f"Instrutor {dto.instructor_id} não encontrado")

        # 2. Se já estiver conectado, retornar status atual
        if instructor_profile.has_mp_account:
            return GatewayConnectResponseDTO(
                account_id=instructor_profile.mp_user_id,
                onboarding_url="",
                is_connected=True,
            )

        # 3. Na Fase 1/4, o link de autorização será gerado via IPaymentGateway
        # TODO: Implementar geração de link OAuth no MercadoPagoGateway
        # Por enquanto retornamos um placeholder para manter o sistema funcional
        return GatewayConnectResponseDTO(
            account_id="", # Será preenchido após o callback
            onboarding_url="https://godrive.com/api/v1/oauth/mercadopago/authorize",
            is_connected=False,
        )
