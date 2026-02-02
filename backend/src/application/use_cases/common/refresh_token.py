"""
Refresh Token Use Case

Caso de uso para renovação de tokens com rotação obrigatória.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

from src.application.dtos.auth_dtos import RefreshTokenDTO, TokenPairDTO
from src.domain.entities.refresh_token import RefreshToken
from src.domain.exceptions import (
    InvalidTokenException,
    TokenExpiredException,
    TokenRevokedException,
    UserNotFoundException,
)
from src.domain.interfaces.auth_service import IAuthService
from src.domain.interfaces.token_repository import ITokenRepository
from src.domain.interfaces.user_repository import IUserRepository


@dataclass
class RefreshTokenUseCase:
    """
    Caso de uso para rotação de refresh tokens.

    Implementa rotação obrigatória conforme PROJECT_GUIDELINES.md:
    cada uso gera um novo token e invalida o anterior.

    Fluxo:
        1. Buscar token pelo hash
        2. Verificar se não expirou
        3. Verificar se não foi revogado
        4. Revogar token atual (rotação)
        5. Gerar novo par de tokens
        6. Persistir novo refresh token
        7. Retornar novo par
    """

    user_repository: IUserRepository
    token_repository: ITokenRepository
    auth_service: IAuthService
    refresh_token_expire_days: int = 7

    async def execute(self, dto: RefreshTokenDTO) -> TokenPairDTO:
        """
        Executa a renovação de tokens.

        Args:
            dto: Refresh token atual.

        Returns:
            TokenPairDTO: Novo par de tokens.

        Raises:
            InvalidTokenException: Se token não existir.
            TokenExpiredException: Se token estiver expirado.
            TokenRevokedException: Se token já foi revogado.
            UserNotFoundException: Se usuário não existir mais.
        """
        # Hash do token recebido para busca
        token_hash = self.auth_service.hash_token(dto.refresh_token)

        # Buscar token
        stored_token = await self.token_repository.get_by_token_hash(token_hash)
        if stored_token is None:
            raise InvalidTokenException("Token não encontrado")

        # Verificar se está revogado
        if stored_token.is_revoked:
            raise TokenRevokedException()

        # Verificar expiração
        if stored_token.is_expired:
            raise TokenExpiredException()

        # Buscar usuário para validar que ainda existe e está ativo
        user = await self.user_repository.get_by_id(stored_token.user_id)
        if user is None:
            raise UserNotFoundException()

        # Revogar token atual (rotação)
        await self.token_repository.revoke(stored_token.id)

        # Gerar novo access token
        access_token = self.auth_service.create_access_token(
            user_id=user.id,
            user_type=user.user_type,
        )

        # Gerar novo refresh token
        raw_refresh_token = self.auth_service.create_refresh_token()
        new_token_hash = self.auth_service.hash_token(raw_refresh_token)

        # Calcular expiração
        expires_at = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)

        # Criar nova entidade de refresh token
        new_refresh_token = RefreshToken(
            token_hash=new_token_hash,
            user_id=user.id,
            expires_at=expires_at,
        )

        # Persistir novo refresh token
        await self.token_repository.create(new_refresh_token)

        return TokenPairDTO(
            access_token=access_token,
            refresh_token=raw_refresh_token,
        )
