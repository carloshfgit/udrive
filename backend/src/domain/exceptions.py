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


# === Profile Exceptions ===


class InstructorNotFoundException(DomainException):
    """Exceção lançada quando um perfil de instrutor não é encontrado."""

    def __init__(self, identifier: str | None = None) -> None:
        message = (
            f"Perfil de instrutor não encontrado: {identifier}"
            if identifier
            else "Perfil de instrutor não encontrado"
        )
        super().__init__(message, "INSTRUCTOR_NOT_FOUND")


class StudentNotFoundException(DomainException):
    """Exceção lançada quando um perfil de aluno não é encontrado."""

    def __init__(self, identifier: str | None = None) -> None:
        message = (
            f"Perfil de aluno não encontrado: {identifier}"
            if identifier
            else "Perfil de aluno não encontrado"
        )
        super().__init__(message, "STUDENT_NOT_FOUND")


class ProfileAlreadyExistsException(DomainException):
    """Exceção lançada quando tentamos criar um perfil que já existe."""

    def __init__(self, user_id: str | None = None) -> None:
        message = f"Perfil já existe para usuário: {user_id}" if user_id else "Perfil já existe"
        super().__init__(message, "PROFILE_ALREADY_EXISTS")


# === Location Exceptions ===


class InvalidLocationException(DomainException):
    """Exceção lançada quando uma localização é inválida."""

    def __init__(self, reason: str | None = None) -> None:
        message = f"Localização inválida: {reason}" if reason else "Localização inválida"
        super().__init__(message, "INVALID_LOCATION")


class LocationRequiredException(DomainException):
    """Exceção lançada quando localização é obrigatória mas não fornecida."""

    def __init__(self) -> None:
        super().__init__("Localização é obrigatória para esta operação", "LOCATION_REQUIRED")

