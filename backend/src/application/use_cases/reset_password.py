"""
Reset Password Use Case

Caso de uso para recuperação de senha.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import uuid4

from src.application.dtos.auth_dtos import ResetPasswordDTO, ResetPasswordRequestDTO
from src.domain.exceptions import InvalidTokenException, UserNotFoundException
from src.domain.interfaces.auth_service import IAuthService
from src.domain.interfaces.user_repository import IUserRepository


# Armazena tokens temporariamente (em produção usar Redis)
# TODO: Mover para Redis na Fase 6
_reset_tokens: dict[str, tuple[str, datetime]] = {}


@dataclass
class RequestPasswordResetUseCase:
    """
    Caso de uso para solicitar reset de senha.

    Gera um token temporário e armazena para validação posterior.
    O envio de email será implementado na Fase 6 (Notificações).
    """

    user_repository: IUserRepository

    async def execute(self, dto: ResetPasswordRequestDTO) -> str | None:
        """
        Solicita reset de senha.

        Args:
            dto: Email do usuário.

        Returns:
            str | None: Token de reset (para testes). Em produção, retorna None
                       e envia email.
        """
        # Verificar se usuário existe
        user = await self.user_repository.get_by_email(dto.email)
        if user is None:
            # Por segurança, não informamos se o email existe ou não
            return None

        # Gerar token de reset
        reset_token = str(uuid4())

        # Armazenar com expiração de 1 hora
        expires_at = datetime.utcnow() + timedelta(hours=1)
        _reset_tokens[reset_token] = (user.email, expires_at)

        # TODO: Enviar email (Fase 6)
        # Por enquanto retorna o token para testes
        return reset_token


@dataclass
class ResetPasswordUseCase:
    """
    Caso de uso para executar reset de senha.

    Valida o token e atualiza a senha do usuário.
    """

    user_repository: IUserRepository
    auth_service: IAuthService

    async def execute(self, dto: ResetPasswordDTO) -> bool:
        """
        Executa o reset de senha.

        Args:
            dto: Token e nova senha.

        Returns:
            bool: True se senha foi atualizada.

        Raises:
            InvalidTokenException: Se token for inválido ou expirado.
            UserNotFoundException: Se usuário não existir mais.
        """
        # Buscar token
        if dto.token not in _reset_tokens:
            raise InvalidTokenException("Token de reset não encontrado")

        email, expires_at = _reset_tokens[dto.token]

        # Verificar expiração
        if datetime.utcnow() > expires_at:
            del _reset_tokens[dto.token]
            raise InvalidTokenException("Token de reset expirado")

        # Buscar usuário
        user = await self.user_repository.get_by_email(email)
        if user is None:
            raise UserNotFoundException(email)

        # Atualizar senha
        new_hashed_password = self.auth_service.hash_password(dto.new_password)
        user.update_password(new_hashed_password)

        # Persistir
        await self.user_repository.update(user)

        # Remover token usado
        del _reset_tokens[dto.token]

        return True
