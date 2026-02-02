"""
Login User Use Case

Caso de uso para autenticação de usuários.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

from src.application.dtos.auth_dtos import LoginDTO, TokenPairDTO
from src.domain.entities.refresh_token import RefreshToken
from src.domain.exceptions import (
    InvalidCredentialsException,
    UserInactiveException,
    UserNotFoundException,
)
from src.domain.interfaces.auth_service import IAuthService
from src.domain.interfaces.token_repository import ITokenRepository
from src.domain.interfaces.user_repository import IUserRepository


@dataclass
class LoginUserUseCase:
    """
    Caso de uso para login de usuários.

    Fluxo:
        1. Buscar usuário por email
        2. Verificar senha
        3. Verificar se usuário está ativo
        4. Gerar access token
        5. Gerar e persistir refresh token
        6. Retornar par de tokens
    """

    user_repository: IUserRepository
    token_repository: ITokenRepository
    auth_service: IAuthService
    refresh_token_expire_days: int = 7

    async def execute(self, dto: LoginDTO) -> TokenPairDTO:
        """
        Executa o login de um usuário.

        Args:
            dto: Credenciais de login.

        Returns:
            TokenPairDTO: Par de tokens (access + refresh).

        Raises:
            UserNotFoundException: Se usuário não existir.
            InvalidCredentialsException: Se senha estiver incorreta.
            UserInactiveException: Se usuário estiver inativo.
        """
        # Buscar usuário
        user = await self.user_repository.get_by_email(dto.email)
        if user is None:
            raise UserNotFoundException(dto.email)

        # Verificar senha
        if not self.auth_service.verify_password(dto.password, user.hashed_password):
            raise InvalidCredentialsException()

        # Verificar se está ativo
        if not user.is_active:
            raise UserInactiveException()

        # Gerar access token
        access_token = self.auth_service.create_access_token(
            user_id=user.id,
            user_type=user.user_type,
        )

        # Gerar refresh token
        raw_refresh_token = self.auth_service.create_refresh_token()
        token_hash = self.auth_service.hash_token(raw_refresh_token)

        # Calcular expiração
        expires_at = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)

        # Criar entidade de refresh token
        refresh_token_entity = RefreshToken(
            token_hash=token_hash,
            user_id=user.id,
            expires_at=expires_at,
        )

        # Persistir refresh token
        await self.token_repository.create(refresh_token_entity)

        return TokenPairDTO(
            access_token=access_token,
            refresh_token=raw_refresh_token,
        )
