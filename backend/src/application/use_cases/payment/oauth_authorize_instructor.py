"""
OAuthAuthorizeInstructor Use Case

Gera a URL de autorização OAuth do Mercado Pago para o instrutor vincular sua conta.
"""

import json
import base64
from urllib.parse import urlencode
from uuid import UUID

from src.application.dtos.payment_dtos import OAuthAuthorizeResponseDTO
from src.domain.exceptions import InstructorNotFoundException
from src.domain.interfaces.instructor_repository import IInstructorRepository
from src.infrastructure.config import Settings


class OAuthAuthorizeInstructorUseCase:
    """Gera URL OAuth para o instrutor vincular sua conta Mercado Pago."""

    MP_AUTH_URL = "https://auth.mercadopago.com/authorization"

    def __init__(
        self,
        instructor_repository: IInstructorRepository,
        settings: Settings,
    ) -> None:
        self.instructor_repository = instructor_repository
        self.settings = settings

    async def execute(
        self, instructor_user_id: UUID, return_url: str | None = None
    ) -> OAuthAuthorizeResponseDTO:
        """
        Gera a URL de autorização OAuth.

        Args:
            instructor_user_id: ID do usuário instrutor.
            return_url: URL para onde redirecionar o app após a vinculação.

        Returns:
            OAuthAuthorizeResponseDTO com a URL para redirecionar o instrutor.

        Raises:
            InstructorNotFoundException: Se o instrutor não for encontrado.
            ValueError: Se o instrutor já tiver conta MP vinculada.
        """
        # 1. Buscar instrutor
        instructor = await self.instructor_repository.get_by_user_id(instructor_user_id)
        if instructor is None:
            raise InstructorNotFoundException(instructor_user_id)

        # 2. Verificar se já está conectado
        if instructor.has_mp_account:
            raise ValueError(
                f"Instrutor {instructor_user_id} já possui conta Mercado Pago vinculada"
            )

        # 3. Montar URL OAuth
        # Codificamos o user_id e a return_url no state para recuperar no callback
        state_data = {"u": str(instructor_user_id)}
        if return_url:
            state_data["r"] = return_url

        state_json = json.dumps(state_data)
        state = base64.urlsafe_b64encode(state_json.encode()).decode().strip("=")

        params = {
            "client_id": self.settings.mp_client_id,
            "response_type": "code",
            "platform_id": "mp",
            "redirect_uri": self.settings.mp_redirect_uri,
            "state": state,
        }

        authorization_url = f"{self.MP_AUTH_URL}?{urlencode(params)}"

        return OAuthAuthorizeResponseDTO(
            authorization_url=authorization_url,
            state=state,
        )
