"""
Auth Service Interface

Define o contrato para operações de autenticação.
"""

from typing import Protocol
from uuid import UUID

from src.domain.entities.user_type import UserType


class IAuthService(Protocol):
    """
    Interface para serviço de autenticação.

    Encapsula operações de hash de senha e geração/validação de tokens JWT.
    """

    def hash_password(self, password: str) -> str:
        """
        Gera hash seguro de uma senha.

        Args:
            password: Senha em texto plano.

        Returns:
            str: Hash da senha (bcrypt).
        """
        ...

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verifica se uma senha corresponde ao hash.

        Args:
            password: Senha em texto plano.
            hashed_password: Hash armazenado.

        Returns:
            bool: True se corresponde, False caso contrário.
        """
        ...

    def create_access_token(
        self,
        user_id: UUID,
        user_type: UserType,
        expires_minutes: int | None = None,
    ) -> str:
        """
        Cria um access token JWT.

        Args:
            user_id: UUID do usuário.
            user_type: Tipo do usuário.
            expires_minutes: Tempo de expiração (padrão: 15 min).

        Returns:
            str: Token JWT assinado.
        """
        ...

    def create_refresh_token(self) -> str:
        """
        Gera um refresh token aleatório.

        Returns:
            str: Token aleatório seguro.
        """
        ...

    def hash_token(self, token: str) -> str:
        """
        Gera hash de um refresh token para armazenamento.

        Args:
            token: Token em texto plano.

        Returns:
            str: Hash do token.
        """
        ...

    def decode_access_token(self, token: str) -> dict:
        """
        Decodifica e valida um access token JWT.

        Args:
            token: Token JWT.

        Returns:
            dict: Payload do token.

        Raises:
            InvalidTokenException: Se token for inválido.
            TokenExpiredException: Se token estiver expirado.
        """
        ...
