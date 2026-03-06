"""
Admin Users Router

Endpoints para gerenciamento de usuários pelo administrador.
"""

from uuid import UUID

import structlog
from fastapi import APIRouter, HTTPException, Query, status

from src.application.dtos.admin_user_dtos import (
    ListUsersDTO,
    SearchUsersDTO,
    ToggleUserStatusDTO,
)
from src.application.use_cases.admin_users.get_user_details import (
    GetUserDetailsUseCase,
)
from src.application.use_cases.admin_users.list_users import ListUsersUseCase
from src.application.use_cases.admin_users.search_users import SearchUsersUseCase
from src.application.use_cases.admin_users.toggle_user_status import (
    ToggleUserStatusUseCase,
    UserNotFoundException,
)
from src.interface.api.dependencies import CurrentAdmin, UserRepo
from src.interface.api.schemas.admin_user_schemas import (
    UserAdminResponse,
    UserListResponse,
)

logger = structlog.get_logger()

router = APIRouter(prefix="/users", tags=["Admin - Users"])


@router.get(
    "",
    response_model=UserListResponse,
    summary="Listar usuários",
    description="Lista usuários com filtros por tipo, status e paginação.",
)
async def list_users(
    current_user: CurrentAdmin,
    user_repo: UserRepo,
    user_type: str | None = Query(
        None,
        description="Filtro por tipo: student, instructor, admin",
    ),
    is_active: bool | None = Query(
        None,
        description="Filtro por status: true (ativos), false (inativos)",
    ),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> UserListResponse:
    """Lista usuários para o painel administrativo."""
    use_case = ListUsersUseCase(user_repository=user_repo)

    offset = (page - 1) * limit
    dto = ListUsersDTO(
        user_type=user_type,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )

    result = await use_case.execute(dto)

    return UserListResponse(
        users=[UserAdminResponse.model_validate(u.__dict__) for u in result.users],
        total_count=result.total_count,
        limit=result.limit,
        offset=result.offset,
        has_more=result.has_more,
    )


@router.get(
    "/search",
    response_model=list[UserAdminResponse],
    summary="Buscar usuários",
    description="Busca usuários por nome, email ou CPF.",
)
async def search_users(
    current_user: CurrentAdmin,
    user_repo: UserRepo,
    q: str = Query(
        ...,
        min_length=2,
        description="Texto de busca (mínimo 2 caracteres)",
    ),
    limit: int = Query(20, ge=1, le=50),
) -> list[UserAdminResponse]:
    """Busca usuários por nome, email ou CPF."""
    use_case = SearchUsersUseCase(user_repository=user_repo)

    dto = SearchUsersDTO(query=q, limit=limit)
    results = await use_case.execute(dto)

    return [UserAdminResponse.model_validate(u.__dict__) for u in results]


@router.get(
    "/{user_id}",
    response_model=UserAdminResponse,
    summary="Detalhes do usuário",
    description="Obtém detalhes completos de um usuário.",
)
async def get_user_details(
    user_id: UUID,
    current_user: CurrentAdmin,
    user_repo: UserRepo,
) -> UserAdminResponse:
    """Obtém detalhes de um usuário específico."""
    use_case = GetUserDetailsUseCase(user_repository=user_repo)
    result = await use_case.execute(user_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )

    return UserAdminResponse.model_validate(result.__dict__)


@router.patch(
    "/{user_id}/status",
    response_model=UserAdminResponse,
    summary="Ativar/Desativar usuário",
    description="Alterna o status ativo/inativo de um usuário.",
)
async def toggle_user_status(
    user_id: UUID,
    current_user: CurrentAdmin,
    user_repo: UserRepo,
) -> UserAdminResponse:
    """Ativa ou desativa um usuário."""
    use_case = ToggleUserStatusUseCase(user_repository=user_repo)

    dto = ToggleUserStatusDTO(
        user_id=user_id,
        admin_id=current_user.id,
    )

    try:
        result = await use_case.execute(dto)
        return UserAdminResponse.model_validate(result.__dict__)
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )
