"""
Auth Service Implementation

Implementação do serviço de autenticação com JWT e bcrypt.
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

import bcrypt
from jose import JWTError, jwt

from src.domain.entities.user_type import UserType
from src.domain.exceptions import InvalidTokenException, TokenExpiredException
from src.infrastructure.config import settings


class AuthServiceImpl:
    """
    Implementação do serviço de autenticação.

    Usa bcrypt para hash de senhas e python-jose para JWT.
    Configurações carregadas de settings (config.py).
    """

    def __init__(
        self,
        secret_key: str | None = None,
        algorithm: str | None = None,
        access_token_expire_minutes: int | None = None,
    ) -> None:
        """
        Inicializa o serviço.

        Args:
            secret_key: Chave secreta para JWT (padrão: settings).
            algorithm: Algoritmo JWT (padrão: settings).
            access_token_expire_minutes: Tempo de expiração (padrão: settings).
        """
        self._secret_key = secret_key or settings.jwt_secret_key
        self._algorithm = algorithm or settings.jwt_algorithm
        self._access_token_expire_minutes = (
            access_token_expire_minutes or settings.access_token_expire_minutes
        )

    def hash_password(self, password: str) -> str:
        """
        Gera hash seguro de uma senha usando bcrypt.

        Args:
            password: Senha em texto plano.

        Returns:
            str: Hash da senha.
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verifica se uma senha corresponde ao hash.

        Args:
            password: Senha em texto plano.
            hashed_password: Hash armazenado.

        Returns:
            bool: True se corresponde.
        """
        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )

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
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=expires_minutes or self._access_token_expire_minutes
        )

        payload = {
            "sub": str(user_id),
            "type": user_type.value,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }

        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def create_refresh_token(self) -> str:
        """
        Gera um refresh token aleatório seguro.

        Returns:
            str: Token aleatório (32 bytes hex).
        """
        return secrets.token_hex(32)

    def hash_token(self, token: str) -> str:
        """
        Gera hash de um refresh token para armazenamento.

        Usa SHA-256 (mais rápido que bcrypt, adequado para tokens aleatórios).

        Args:
            token: Token em texto plano.

        Returns:
            str: Hash SHA-256 do token.
        """
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def decode_access_token(self, token: str) -> dict:
        """
        Decodifica e valida um access token JWT.

        Args:
            token: Token JWT.

        Returns:
            dict: Payload do token com 'sub' (user_id) e 'type' (user_type).

        Raises:
            InvalidTokenException: Se token for inválido.
            TokenExpiredException: Se token estiver expirado.
        """
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
            )
            return {
                "user_id": UUID(payload["sub"]),
                "user_type": UserType(payload["type"]),
            }
        except jwt.ExpiredSignatureError as err:
            raise TokenExpiredException() from err
        except JWTError as err:
            raise InvalidTokenException("Token JWT inválido") from err
        except (KeyError, ValueError) as err:
            raise InvalidTokenException("Payload do token inválido") from err
