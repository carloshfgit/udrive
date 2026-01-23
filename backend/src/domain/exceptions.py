"""
Domain Exceptions

Exceções customizadas do domínio para tratamento de erros de negócio.
"""


class DomainException(Exception):
    """Exceção base do domínio."""

    def __init__(self, message: str, code: str | None = None) -> None:
        self.message = message
        self.code = code or self.__class__.__name__
        super().__init__(self.message)


# === User Exceptions ===


class UserNotFoundException(DomainException):
    """Exceção lançada quando um usuário não é encontrado."""

    def __init__(self, identifier: str | None = None) -> None:
        message = f"Usuário não encontrado: {identifier}" if identifier else "Usuário não encontrado"
        super().__init__(message, "USER_NOT_FOUND")


class UserAlreadyExistsException(DomainException):
    """Exceção lançada quando tentamos criar um usuário que já existe."""

    def __init__(self, email: str | None = None) -> None:
        message = f"Usuário já existe: {email}" if email else "Usuário já existe"
        super().__init__(message, "USER_ALREADY_EXISTS")


class InvalidCredentialsException(DomainException):
    """Exceção lançada quando as credenciais são inválidas."""

    def __init__(self) -> None:
        super().__init__("Email ou senha inválidos", "INVALID_CREDENTIALS")


class UserInactiveException(DomainException):
    """Exceção lançada quando o usuário está inativo."""

    def __init__(self) -> None:
        super().__init__("Usuário está inativo", "USER_INACTIVE")


# === Token Exceptions ===


class TokenExpiredException(DomainException):
    """Exceção lançada quando um token está expirado."""

    def __init__(self) -> None:
        super().__init__("Token expirado", "TOKEN_EXPIRED")


class TokenRevokedException(DomainException):
    """Exceção lançada quando um token foi revogado."""

    def __init__(self) -> None:
        super().__init__("Token revogado", "TOKEN_REVOKED")


class InvalidTokenException(DomainException):
    """Exceção lançada quando um token é inválido."""

    def __init__(self, reason: str | None = None) -> None:
        message = f"Token inválido: {reason}" if reason else "Token inválido"
        super().__init__(message, "INVALID_TOKEN")
