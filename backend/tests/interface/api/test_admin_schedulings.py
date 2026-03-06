"""
Tests for Admin Scheduling Endpoints
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from datetime import datetime, timedelta

from src.infrastructure.db.models.user_model import UserModel
from src.infrastructure.db.models.scheduling_model import SchedulingModel
from src.domain.entities.user_type import UserType
from src.domain.entities.scheduling_status import SchedulingStatus
from src.infrastructure.services.auth_service_impl import AuthServiceImpl

@pytest.fixture
async def admin_token(db_session: AsyncSession) -> str:
    """Cria um administrador e retorna seu token."""
    auth_service = AuthServiceImpl()
    admin_id = uuid4()
    admin = UserModel(
        id=admin_id,
        email="admin_sched@test.com",
        full_name="Admin Sched User",
        hashed_password="hashed_password",
        user_type=UserType.ADMIN.value,
        is_active=True,
        is_verified=True
    )
    db_session.add(admin)
    await db_session.commit()
    
    return auth_service.create_access_token(user_id=admin_id, user_type=UserType.ADMIN)

@pytest.mark.asyncio
async def test_list_schedulings_as_admin(client: AsyncClient, admin_token: str, db_session: AsyncSession):
    """Testa a listagem de todos os agendamentos como administrador."""
    # Criar um aluno e um instrutor
    student_id = uuid4()
    instructor_id = uuid4()
    student = UserModel(id=student_id, email="student_s@test.com", full_name="Student", hashed_password="h", user_type=UserType.STUDENT.value)
    instructor = UserModel(id=instructor_id, email="instr_s@test.com", full_name="Instructor", hashed_password="h", user_type=UserType.INSTRUCTOR.value)
    
    # Criar um agendamento
    scheduling = SchedulingModel(
        id=uuid4(),
        student_id=student_id,
        instructor_id=instructor_id,
        scheduled_datetime=datetime.utcnow() + timedelta(days=1),
        duration_minutes=60,
        price=100.0,
        status=SchedulingStatus.CONFIRMED.value
    )
    
    db_session.add_all([student, instructor, scheduling])
    await db_session.commit()

    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await client.get("/api/v1/admin/schedulings", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "schedulings" in data
    assert data["total_count"] >= 1
    assert any(s["id"] == str(scheduling.id) for s in data["schedulings"])

@pytest.mark.asyncio
async def test_get_scheduling_details_admin(client: AsyncClient, admin_token: str, db_session: AsyncSession):
    """Testa buscar detalhes de um agendamento."""
    student_id = uuid4()
    instructor_id = uuid4()
    student = UserModel(id=student_id, email="student_d@test.com", full_name="Student Detail", hashed_password="h", user_type=UserType.STUDENT.value)
    instructor = UserModel(id=instructor_id, email="instr_d@test.com", full_name="Instructor Detail", hashed_password="h", user_type=UserType.INSTRUCTOR.value)
    
    scheduling = SchedulingModel(
        id=uuid4(),
        student_id=student_id,
        instructor_id=instructor_id,
        scheduled_datetime=datetime.utcnow() + timedelta(days=2),
        duration_minutes=60,
        price=150.0,
        status=SchedulingStatus.CONFIRMED.value
    )
    
    db_session.add_all([student, instructor, scheduling])
    await db_session.commit()

    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await client.get(f"/api/v1/admin/schedulings/{scheduling.id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(scheduling.id)
    assert data["student_name"] == "Student Detail"
    assert data["instructor_name"] == "Instructor Detail"

@pytest.mark.asyncio
async def test_admin_cancel_scheduling(client: AsyncClient, admin_token: str, db_session: AsyncSession):
    """Testa o cancelamento administrativo forçado."""
    student_id = uuid4()
    instructor_id = uuid4()
    student = UserModel(id=student_id, email="student_c@test.com", full_name="Student Cancel", hashed_password="h", user_type=UserType.STUDENT.value)
    instructor = UserModel(id=instructor_id, email="instr_c@test.com", full_name="Instructor Cancel", hashed_password="h", user_type=UserType.INSTRUCTOR.value)
    
    scheduling = SchedulingModel(
        id=uuid4(),
        student_id=student_id,
        instructor_id=instructor_id,
        scheduled_datetime=datetime.utcnow() + timedelta(hours=1), # Em breve
        duration_minutes=60,
        price=10.0,
        status=SchedulingStatus.CONFIRMED.value
    )
    
    db_session.add_all([student, instructor, scheduling])
    await db_session.commit()

    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {"reason": "Intervenção administrativa por má conduta"}
    
    response = await client.patch(f"/api/v1/admin/schedulings/{scheduling.id}/cancel", headers=headers, json=payload)
    
    assert response.status_code == 200
    assert response.json()["status"] == SchedulingStatus.CANCELLED.value

@pytest.mark.asyncio
async def test_admin_schedulings_require_admin(client: AsyncClient, db_session: AsyncSession):
    """Testa bloqueio de não-admins."""
    auth_service = AuthServiceImpl()
    student_id = uuid4()
    student = UserModel(id=student_id, email="student_unauth@test.com", full_name="Student", hashed_password="h", user_type=UserType.STUDENT.value)
    db_session.add(student)
    await db_session.commit()
    
    token = auth_service.create_access_token(user_id=student_id, user_type=UserType.STUDENT)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = await client.get("/api/v1/admin/schedulings", headers=headers)
    assert response.status_code == 403
