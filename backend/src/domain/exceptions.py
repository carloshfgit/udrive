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


# === Scheduling Exceptions ===


class SchedulingNotFoundException(DomainException):
    """Exceção lançada quando um agendamento não é encontrado."""

    def __init__(self, identifier: str | None = None) -> None:
        message = (
            f"Agendamento não encontrado: {identifier}"
            if identifier
            else "Agendamento não encontrado"
        )
        super().__init__(message, "SCHEDULING_NOT_FOUND")


class SchedulingConflictException(DomainException):
    """Exceção lançada quando há conflito de horário no agendamento."""

    def __init__(self, reason: str | None = None) -> None:
        message = (
            f"Conflito de horário: {reason}"
            if reason
            else "Já existe um agendamento neste horário"
        )
        super().__init__(message, "SCHEDULING_CONFLICT")


class UnavailableSlotException(DomainException):
    """Exceção lançada quando o slot de horário não está disponível."""

    def __init__(self, reason: str | None = None) -> None:
        message = (
            f"Horário indisponível: {reason}"
            if reason
            else "O instrutor não está disponível neste horário"
        )
        super().__init__(message, "UNAVAILABLE_SLOT")


class SchedulingAlreadyCancelledException(DomainException):
    """Exceção lançada quando tentamos cancelar um agendamento já cancelado."""

    def __init__(self) -> None:
        super().__init__("Agendamento já foi cancelado", "SCHEDULING_ALREADY_CANCELLED")


class SchedulingAlreadyCompletedException(DomainException):
    """Exceção lançada quando tentamos modificar um agendamento já concluído."""

    def __init__(self) -> None:
        super().__init__("Agendamento já foi concluído", "SCHEDULING_ALREADY_COMPLETED")


class InvalidSchedulingStateException(DomainException):
    """Exceção lançada quando o estado do agendamento é inválido para a operação."""

    def __init__(self, current_state: str, expected_state: str | None = None) -> None:
        if expected_state:
            message = f"Estado inválido: esperado '{expected_state}', atual '{current_state}'"
        else:
            message = f"Operação não permitida no estado atual: {current_state}"
        super().__init__(message, "INVALID_SCHEDULING_STATE")


class LessonNotFinishedException(DomainException):
    """Exceção lançada quando tenta concluir uma aula que ainda não acabou."""

    def __init__(self, end_time: str) -> None:
        super().__init__(
            f"A aula ainda não terminou. Você só poderá concluí-la após o horário de término previsto ({end_time}).",
            "LESSON_NOT_FINISHED"
        )


class CompletionConfirmationMissingException(DomainException):
    """Exceção lançada quando o instrutor tenta concluir mas o aluno não confirmou."""

    def __init__(self) -> None:
        super().__init__(
            "Solicite ao aluno para confirmar a conclusão da aula no aplicativo.",
            "COMPLETION_CONFIRMATION_MISSING"
        )


class LessonNotStartedException(DomainException):
    """Exceção lançada quando tenta concluir uma aula que ainda não começou."""

    def __init__(self) -> None:
        super().__init__(
            "Solicite ao aluno para confirmar a conclusão da aula no aplicativo.",
            "LESSON_NOT_STARTED"
        )


# === Availability Exceptions ===


class AvailabilityNotFoundException(DomainException):
    """Exceção lançada quando uma disponibilidade não é encontrada."""

    def __init__(self, identifier: str | None = None) -> None:
        message = (
            f"Disponibilidade não encontrada: {identifier}"
            if identifier
            else "Disponibilidade não encontrada"
        )
        super().__init__(message, "AVAILABILITY_NOT_FOUND")


class InvalidAvailabilityTimeException(DomainException):
    """Exceção lançada quando o intervalo de tempo é inválido."""

    def __init__(self, reason: str | None = None) -> None:
        message = (
            f"Intervalo de tempo inválido: {reason}"
            if reason
            else "Hora de início deve ser anterior à hora de término"
        )
        super().__init__(message, "INVALID_AVAILABILITY_TIME")


class AvailabilityOverlapException(DomainException):
    """Exceção lançada quando há sobreposição de slots de disponibilidade."""

    def __init__(self) -> None:
        super().__init__(
            "Já existe um slot de disponibilidade neste horário",
            "AVAILABILITY_OVERLAP"
        )


# === Payment Exceptions ===


class PaymentNotFoundException(DomainException):
    """Exceção lançada quando um pagamento não é encontrado."""

    def __init__(self, identifier: str | None = None) -> None:
        message = (
            f"Pagamento não encontrado: {identifier}"
            if identifier
            else "Pagamento não encontrado"
        )
        super().__init__(message, "PAYMENT_NOT_FOUND")


class PaymentFailedException(DomainException):
    """Exceção lançada quando um pagamento falha no gateway."""

    def __init__(self, reason: str | None = None) -> None:
        message = (
            f"Falha no pagamento: {reason}"
            if reason
            else "Falha ao processar pagamento"
        )
        super().__init__(message, "PAYMENT_FAILED")


class RefundException(DomainException):
    """Exceção lançada quando há erro no reembolso."""

    def __init__(self, reason: str | None = None) -> None:
        message = (
            f"Erro no reembolso: {reason}"
            if reason
            else "Erro ao processar reembolso"
        )
        super().__init__(message, "REFUND_ERROR")


class InvalidRefundAmountException(DomainException):
    """Exceção lançada quando o valor de reembolso é inválido."""

    def __init__(self, reason: str | None = None) -> None:
        message = (
            f"Valor de reembolso inválido: {reason}"
            if reason
            else "Valor de reembolso inválido"
        )
        super().__init__(message, "INVALID_REFUND_AMOUNT")


class GatewayAccountNotConnectedException(DomainException):
    """Exceção lançada quando instrutor não tem conta de pagamento conectada."""

    def __init__(self, instructor_id: str | None = None) -> None:
        message = (
            f"Instrutor {instructor_id} não possui conta de pagamento conectada"
            if instructor_id
            else "Instrutor não possui conta de pagamento conectada"
        )
        super().__init__(message, "PAYMENT_ACCOUNT_NOT_CONNECTED")


class PaymentAlreadyProcessedException(DomainException):
    """Exceção lançada quando pagamento já foi processado."""

    def __init__(self) -> None:
        super().__init__(
            "Pagamento já foi processado",
            "PAYMENT_ALREADY_PROCESSED"
        )


# === Chat Exceptions ===


class ForbiddenContentException(DomainException):
    """Exceção lançada quando o conteúdo da mensagem viola as regras de segurança."""

    def __init__(self, reason: str | None = None) -> None:
        message = (
            f"Conteúdo proibido: {reason}"
            if reason
            else "A mensagem contém conteúdo não permitido pela plataforma."
        )
        super().__init__(message, "FORBIDDEN_CONTENT")


class ActiveSchedulingRequiredException(DomainException):
    """Exceção lançada quando tenta-se enviar mensagem sem agendamento ativo."""

    def __init__(self) -> None:
        super().__init__(
            "Você só pode enviar mensagens para usuários com quem possui agendamentos ativos.",
            "ACTIVE_SCHEDULING_REQUIRED",
        )
