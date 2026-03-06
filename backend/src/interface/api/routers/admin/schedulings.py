"""
Admin Schedulings Router

Endpoints para gerenciamento de agendamentos pelo administrador.
"""

from datetime import datetime
from uuid import UUID

import structlog
from fastapi import APIRouter, HTTPException, Query, status

from src.application.dtos.admin_scheduling_dtos import (
    AdminCancelSchedulingDTO,
    ListAllSchedulingsDTO,
)
from src.application.use_cases.admin_schedulings.admin_cancel_scheduling import (
    AdminCancelSchedulingUseCase,
    SchedulingNotFoundException,
)
from src.application.use_cases.admin_schedulings.get_scheduling_details import (
    GetSchedulingDetailsUseCase,
)
from src.application.use_cases.admin_schedulings.list_all_schedulings import (
    ListAllSchedulingsUseCase,
)
from src.domain.entities.scheduling_status import SchedulingStatus
from src.interface.api.dependencies import CurrentAdmin, SchedulingRepo
from src.interface.api.schemas.admin_scheduling_schemas import (
    AdminCancelRequest,
    SchedulingAdminResponse,
    SchedulingListResponse,
)

logger = structlog.get_logger()

router = APIRouter(prefix="/schedulings", tags=["Admin - Schedulings"])


@router.get(
    "",
    response_model=SchedulingListResponse,
    summary="Listar todos os agendamentos",
    description="Lista todos os agendamentos do sistema com diversos filtros.",
)
async def list_all_schedulings(
    current_user: CurrentAdmin,
    scheduling_repo: SchedulingRepo,
    status_filter: SchedulingStatus | None = Query(None, alias="status"),
    student_id: UUID | None = None,
    instructor_id: UUID | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> SchedulingListResponse:
    """Lista agendamentos para o painel administrativo."""
    use_case = ListAllSchedulingsUseCase(scheduling_repository=scheduling_repo)

    offset = (page - 1) * limit
    dto = ListAllSchedulingsDTO(
        status=status_filter,
        student_id=student_id,
        instructor_id=instructor_id,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )

    result = await use_case.execute(dto)

    return SchedulingListResponse(
        schedulings=[
            SchedulingAdminResponse.model_validate(s.__dict__)
            for s in result.schedulings
        ],
        total_count=result.total_count,
        limit=result.limit,
        offset=result.offset,
        has_more=result.has_more,
    )


@router.get(
    "/{scheduling_id}",
    response_model=SchedulingAdminResponse,
    summary="Detalhes do agendamento",
    description="Obtém detalhes completos de um agendamento específico.",
)
async def get_scheduling_details(
    scheduling_id: UUID,
    current_user: CurrentAdmin,
    scheduling_repo: SchedulingRepo,
) -> SchedulingAdminResponse:
    """Obtém detalhes de um agendamento."""
    use_case = GetSchedulingDetailsUseCase(scheduling_repository=scheduling_repo)
    result = await use_case.execute(scheduling_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado",
        )

    return SchedulingAdminResponse.model_validate(result.__dict__)


@router.patch(
    "/{scheduling_id}/cancel",
    response_model=SchedulingAdminResponse,
    summary="Cancelar agendamento (Admin)",
    description="Cancela um agendamento por intervenção administrativa.",
)
async def admin_cancel_scheduling(
    scheduling_id: UUID,
    request: AdminCancelRequest,
    current_user: CurrentAdmin,
    scheduling_repo: SchedulingRepo,
) -> SchedulingAdminResponse:
    """Cancela um agendamento como admin."""
    use_case = AdminCancelSchedulingUseCase(scheduling_repository=scheduling_repo)

    dto = AdminCancelSchedulingDTO(
        scheduling_id=scheduling_id,
        admin_id=current_user.id,
        reason=request.reason,
    )

    try:
        result = await use_case.execute(dto)
        return SchedulingAdminResponse.model_validate(result.__dict__)
    except SchedulingNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado",
        )
