"""
Authentication Router

Endpoints REST para operações de autenticação.
Segue Clean Architecture: recebe requisição, converte para DTO,
executa caso de uso e retorna resposta.
"""

from fastapi import APIRouter, status

from src.application.dtos.auth_dtos import (
    LoginDTO,
    RefreshTokenDTO,
    RegisterUserDTO,
    ResetPasswordDTO,
    ResetPasswordRequestDTO,
)
from src.application.use_cases.login_user import LoginUserUseCase
from src.application.use_cases.logout_user import LogoutUserUseCase
from src.application.use_cases.refresh_token import RefreshTokenUseCase
from src.application.use_cases.register_user import RegisterUserUseCase
from src.application.use_cases.reset_password import (
    RequestPasswordResetUseCase,
    ResetPasswordUseCase,
)
from src.domain.entities.user_type import UserType
from src.interface.api.dependencies import AuthService, CurrentUser, TokenRepo, UserRepo
from src.interface.api.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obter usuário atual",
    description="Retorna os dados do usuário autenticado.",
)
async def me(current_user: CurrentUser) -> UserResponse:
    """Retorna os dados do usuário autenticado."""
    return current_user


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar novo usuário",
    description="Cria um novo usuário no sistema (aluno, instrutor ou admin).",
)
async def register(
    request: RegisterRequest,
    user_repo: UserRepo,
    auth_service: AuthService,
) -> UserResponse:
    """Cadastra um novo usuário."""
    use_case = RegisterUserUseCase(
        user_repository=user_repo,
        auth_service=auth_service,
    )

    dto = RegisterUserDTO(
        email=request.email,
        password=request.password,
        full_name=request.full_name,
        user_type=UserType(request.user_type.value),
    )

    user = await use_case.execute(dto)

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        user_type=user.user_type.value,
        is_active=user.is_active,
        is_verified=user.is_verified,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login de usuário",
    description="Autentica um usuário e retorna par de tokens (access + refresh).",
)
async def login(
    request: LoginRequest,
    user_repo: UserRepo,
    token_repo: TokenRepo,
    auth_service: AuthService,
) -> TokenResponse:
    """Autentica um usuário e retorna tokens."""
    use_case = LoginUserUseCase(
        user_repository=user_repo,
        token_repository=token_repo,
        auth_service=auth_service,
    )

    dto = LoginDTO(email=request.email, password=request.password)
    result = await use_case.execute(dto)

    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Renovar tokens",
    description="Renova o par de tokens usando refresh token. Implementa rotação obrigatória.",
)
async def refresh(
    request: RefreshTokenRequest,
    user_repo: UserRepo,
    token_repo: TokenRepo,
    auth_service: AuthService,
) -> TokenResponse:
    """Renova o par de tokens usando o refresh token."""
    use_case = RefreshTokenUseCase(
        user_repository=user_repo,
        token_repository=token_repo,
        auth_service=auth_service,
    )

    dto = RefreshTokenDTO(refresh_token=request.refresh_token)
    result = await use_case.execute(dto)

    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout de usuário",
    description="Invalida o refresh token atual, encerrando a sessão.",
)
async def logout(
    request: RefreshTokenRequest,
    token_repo: TokenRepo,
    auth_service: AuthService,
) -> MessageResponse:
    """Invalida o refresh token (logout)."""
    # Buscar token pelo hash para obter o ID
    token_hash = auth_service.hash_token(request.refresh_token)
    stored_token = await token_repo.get_by_token_hash(token_hash)

    if stored_token is not None:
        use_case = LogoutUserUseCase(token_repository=token_repo)
        await use_case.execute(token_id=stored_token.id)

    # Por segurança, sempre retorna sucesso (não expõe se token existia)
    return MessageResponse(message="Logout realizado com sucesso")


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Solicitar reset de senha",
    description="Envia instruções para reset de senha ao email informado.",
)
async def forgot_password(
    request: ForgotPasswordRequest,
    user_repo: UserRepo,
) -> MessageResponse:
    """Solicita reset de senha (envia email/token)."""
    use_case = RequestPasswordResetUseCase(user_repository=user_repo)
    dto = ResetPasswordRequestDTO(email=request.email)

    # Executar (não expõe se email existe ou não)
    await use_case.execute(dto)

    return MessageResponse(
        message="Se o email estiver cadastrado, você receberá instruções para redefinir sua senha"
    )


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Executar reset de senha",
    description="Redefine a senha usando token de reset válido.",
)
async def reset_password(
    request: ResetPasswordRequest,
    user_repo: UserRepo,
    auth_service: AuthService,
) -> MessageResponse:
    """Executa o reset de senha com token válido."""
    use_case = ResetPasswordUseCase(
        user_repository=user_repo,
        auth_service=auth_service,
    )

    dto = ResetPasswordDTO(token=request.token, new_password=request.new_password)
    await use_case.execute(dto)

    return MessageResponse(message="Senha alterada com sucesso")
