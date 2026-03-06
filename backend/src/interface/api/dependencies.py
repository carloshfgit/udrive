"""
API Dependencies

Sistema de injeção de dependências para desacoplar a API dos repositórios e serviços.
Usa o padrão de Dependency Injection do FastAPI.
"""

from typing import Annotated

from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.domain.exceptions import (
    InvalidTokenException,
    TokenExpiredException,
    UserInactiveException,
    UserNotFoundException,
)
from src.domain.interfaces.auth_service import IAuthService
from src.domain.interfaces.instructor_repository import IInstructorRepository
from src.domain.interfaces.location_service import ILocationService
from src.domain.interfaces.message_repository import IMessageRepository
from src.domain.interfaces.scheduling_repository import ISchedulingRepository
from src.domain.interfaces.review_repository import IReviewRepository
from src.domain.interfaces.availability_repository import IAvailabilityRepository
from src.domain.interfaces.student_repository import IStudentRepository
from src.domain.interfaces.token_repository import ITokenRepository
from src.domain.interfaces.user_repository import IUserRepository
from src.domain.interfaces.payment_repository import IPaymentRepository
from src.domain.interfaces.dispute_repository import IDisputeRepository
from src.infrastructure.db.database import get_db
from src.infrastructure.repositories.instructor_repository_impl import (
    InstructorRepositoryImpl,
)
from src.infrastructure.repositories.review_repository_impl import (
    ReviewRepositoryImpl,
)
from src.infrastructure.repositories.scheduling_repository_impl import (
    SchedulingRepositoryImpl,
)
from src.infrastructure.repositories.availability_repository_impl import (
    AvailabilityRepositoryImpl,
)
from src.infrastructure.repositories.message_repository_impl import (
    MessageRepositoryImpl,
)
from src.infrastructure.repositories.student_repository_impl import (
    StudentRepositoryImpl,
)
from src.infrastructure.repositories.token_repository_impl import TokenRepositoryImpl
from src.infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from src.infrastructure.repositories.payment_repository_impl import PaymentRepositoryImpl
from src.infrastructure.repositories.dispute_repository_impl import (
    DisputeRepositoryImpl,
)
from src.infrastructure.services.auth_service_impl import AuthServiceImpl
from src.infrastructure.services.location_service_impl import LocationServiceImpl
from src.infrastructure.external.redis_cache import RedisCacheService, cache_service


# =============================================================================
# Database Session
# =============================================================================

DBSession = Annotated[AsyncSession, Depends(get_db)]


# =============================================================================
# Repository Dependencies
# =============================================================================


def get_user_repository(session: DBSession) -> IUserRepository:
    """Fornece uma instância do repositório de usuários."""
    return UserRepositoryImpl(session)


def get_token_repository(session: DBSession) -> ITokenRepository:
    """Fornece uma instância do repositório de tokens."""
    return TokenRepositoryImpl(session)


def get_instructor_repository(session: DBSession) -> IInstructorRepository:
    """Fornece uma instância do repositório de instrutores."""
    return InstructorRepositoryImpl(session)


def get_student_repository(session: DBSession) -> IStudentRepository:
    """Fornece uma instância do repositório de alunos."""
    return StudentRepositoryImpl(session)


def get_scheduling_repository(session: DBSession) -> ISchedulingRepository:
    """Fornece uma instância do repositório de agendamentos."""
    return SchedulingRepositoryImpl(session)


def get_payment_repository(session: DBSession) -> IPaymentRepository:
    """Fornece uma instância do repositório de pagamentos."""
    return PaymentRepositoryImpl(session)


def get_availability_repository(session: DBSession) -> IAvailabilityRepository:
    """Fornece uma instância do repositório de disponibilidade."""
    return AvailabilityRepositoryImpl(session)


def get_review_repository(session: DBSession) -> IReviewRepository:
    """Fornece uma instância do repositório de avaliações."""
    return ReviewRepositoryImpl(session)


def get_message_repository(session: DBSession) -> IMessageRepository:
    """Fornece uma instância do repositório de mensagens."""
    return MessageRepositoryImpl(session)


def get_dispute_repository(session: DBSession) -> IDisputeRepository:
    """Fornece uma instância do repositório de disputas."""
    return DisputeRepositoryImpl(session)


# =============================================================================
# Service Dependencies
# =============================================================================


def get_auth_service() -> IAuthService:
    """Fornece uma instância do serviço de autenticação."""
    return AuthServiceImpl()


def get_location_service(
    instructor_repo: Annotated[IInstructorRepository, Depends(get_instructor_repository)],
) -> ILocationService:
    """Fornece uma instância do serviço de geolocalização."""
    return LocationServiceImpl(instructor_repo)


def get_cache_service() -> RedisCacheService:
    """Fornece a instância global do serviço de cache."""
    return cache_service


# =============================================================================
# Authentication Dependencies
# =============================================================================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[IAuthService, Depends(get_auth_service)],
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
) -> User:
    """
    Obtém o usuário autenticado a partir do token JWT.

    Decodifica o token, valida e busca o usuário no banco.

    Raises:
        HTTPException 401: Se token inválido, expirado ou usuário não encontrado.
    """
    try:
        payload = auth_service.decode_access_token(token)
        user_id = payload["user_id"]
    except (InvalidTokenException, TokenExpiredException):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas ou token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    user = await user_repo.get_essential_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Verifica se o usuário autenticado está ativo.

    Raises:
        HTTPException 400: Se usuário inativo.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo",
        )
    return current_user



# =============================================================================
# Permission Dependencies
# =============================================================================


def require_student(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """
    Garante que o usuário autenticado seja um aluno.

    Raises:
        HTTPException 403: Se não for aluno.
    """
    if not current_user.is_student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para alunos",
        )
    return current_user


def require_instructor(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """
    Garante que o usuário autenticado seja um instrutor.

    Raises:
        HTTPException 403: Se não for instrutor.
    """
    if not current_user.is_instructor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para instrutores",
        )
    return current_user


def require_admin(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """
    Garante que o usuário autenticado seja um administrador.

    Raises:
        HTTPException 403: Se não for administrador.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para administradores",
        )
    return current_user


# =============================================================================
# Type Aliases para uso nos endpoints
# =============================================================================

UserRepo = Annotated[IUserRepository, Depends(get_user_repository)]
TokenRepo = Annotated[ITokenRepository, Depends(get_token_repository)]
InstructorRepo = Annotated[IInstructorRepository, Depends(get_instructor_repository)]
StudentRepo = Annotated[IStudentRepository, Depends(get_student_repository)]
SchedulingRepo = Annotated[ISchedulingRepository, Depends(get_scheduling_repository)]
PaymentRepo = Annotated[IPaymentRepository, Depends(get_payment_repository)]
AvailabilityRepo = Annotated[IAvailabilityRepository, Depends(get_availability_repository)]
ReviewRepo = Annotated[IReviewRepository, Depends(get_review_repository)]
AuthService = Annotated[IAuthService, Depends(get_auth_service)]
LocationService = Annotated[ILocationService, Depends(get_location_service)]
CacheService = Annotated[RedisCacheService, Depends(get_cache_service)]
MessageRepo = Annotated[IMessageRepository, Depends(get_message_repository)]
DisputeRepo = Annotated[IDisputeRepository, Depends(get_dispute_repository)]

CurrentUser = Annotated[User, Depends(get_current_active_user)]
CurrentStudent = Annotated[User, Depends(require_student)]
CurrentInstructor = Annotated[User, Depends(require_instructor)]
CurrentAdmin = Annotated[User, Depends(require_admin)]


# =============================================================================
# Use Case Dependencies
# =============================================================================

# Notification Dependencies (definidas antes para uso nas factory functions abaixo)
from src.application.services.notification_service import NotificationService
from src.infrastructure.repositories.notification_repository_impl import (
    NotificationRepositoryImpl,
)
from src.infrastructure.services.push_notification_service import (
    ExpoPushNotificationService,
)
from src.interface.websockets.connection_manager import manager as ws_manager


def get_notification_service(
    session: DBSession,
) -> NotificationService:
    """Fornece o NotificationService com todos os colaboradores injetados."""
    return NotificationService(
        notification_repository=NotificationRepositoryImpl(session),
        push_service=ExpoPushNotificationService(session),
        ws_manager=ws_manager,
    )


NotificationServiceDep = Annotated[NotificationService, Depends(get_notification_service)]


from src.application.use_cases.chat.send_message_use_case import SendMessageUseCase
from src.application.use_cases.chat.get_instructor_conversations_use_case import (
    GetInstructorConversationsUseCase,
)
from src.application.use_cases.chat.get_student_conversations_use_case import (
    GetStudentConversationsUseCase,
)
from src.application.use_cases.chat.get_student_lessons_for_instructor_use_case import (
    GetStudentLessonsForInstructorUseCase,
)
from src.application.use_cases.chat.get_instructor_lessons_for_student_use_case import (
    GetInstructorLessonsForStudentUseCase,
)
from src.application.use_cases.payment.refund_single_payment import RefundSinglePaymentUseCase
from src.application.use_cases.scheduling.resolve_dispute import ResolveDisputeUseCase
from src.application.use_cases.scheduling.scheduling_notification_decorators import (
    NotifyOnResolveDispute,
)


from src.application.use_cases.chat.chat_notification_decorators import NotifyOnSendMessage


def get_send_message_use_case(
    message_repo: MessageRepo,
    scheduling_repo: SchedulingRepo,
    user_repo: UserRepo,
    notification_svc: NotificationServiceDep,
) -> NotifyOnSendMessage:
    wrapped = SendMessageUseCase(message_repo, scheduling_repo, user_repo)
    return NotifyOnSendMessage(
        _wrapped=wrapped,
        _notification_service=notification_svc,
    )


def get_get_instructor_conversations_use_case(
    scheduling_repo: SchedulingRepo,
    message_repo: MessageRepo,
) -> GetInstructorConversationsUseCase:
    return GetInstructorConversationsUseCase(scheduling_repo, message_repo)


def get_get_student_conversations_use_case(
    scheduling_repo: SchedulingRepo,
    message_repo: MessageRepo,
) -> GetStudentConversationsUseCase:
    return GetStudentConversationsUseCase(scheduling_repo, message_repo)


def get_get_student_lessons_for_instructor_use_case(
    scheduling_repo: SchedulingRepo,
) -> GetStudentLessonsForInstructorUseCase:
    return GetStudentLessonsForInstructorUseCase(scheduling_repo)


def get_get_instructor_lessons_for_student_use_case(
    scheduling_repo: SchedulingRepo,
) -> GetInstructorLessonsForStudentUseCase:
    return GetInstructorLessonsForStudentUseCase(scheduling_repo)


def get_refund_single_payment_use_case(
    payment_repo: PaymentRepo,
    transaction_repo: Annotated[DBSession, Depends(get_db)], # Custom injection if needed
    instructor_repo: InstructorRepo,
    scheduling_repo: SchedulingRepo,
) -> RefundSinglePaymentUseCase:
    # Transaction repository impl
    from src.infrastructure.repositories.transaction_repository_impl import TransactionRepositoryImpl
    from src.infrastructure.external.mercadopago_gateway import MercadoPagoGateway
    
    # Nota: O transaction_repo precisa da session
    db_session = transaction_repo # Reutilizando a session injetada
    trans_repo = TransactionRepositoryImpl(db_session)
    gateway = MercadoPagoGateway()
    
    return RefundSinglePaymentUseCase(
        payment_repository=payment_repo,
        transaction_repository=trans_repo,
        instructor_repository=instructor_repo,
        scheduling_repository=scheduling_repo,
        payment_gateway=gateway,
    )


def get_resolve_dispute_use_case(
    dispute_repo: DisputeRepo,
    scheduling_repo: SchedulingRepo,
    payment_repo: PaymentRepo,
    instructor_repo: InstructorRepo,
    notification_svc: NotificationServiceDep,
    session: DBSession,
) -> NotifyOnResolveDispute:
    refund_use_case = get_refund_single_payment_use_case(
        payment_repo, session, instructor_repo, scheduling_repo
    )
    wrapped = ResolveDisputeUseCase(
        dispute_repository=dispute_repo,
        scheduling_repository=scheduling_repo,
        refund_use_case=refund_use_case,
    )
    return NotifyOnResolveDispute(
        _wrapped=wrapped,
        _notification_service=notification_svc,
    )


