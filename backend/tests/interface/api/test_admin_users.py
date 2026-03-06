"""
Tests for Admin User Endpoints
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from src.infrastructure.db.models.user_model import UserModel
from src.domain.entities.user_type import UserType
from src.infrastructure.services.auth_service_impl import AuthServiceImpl

@pytest.fixture
async def admin_token(db_session: AsyncSession) -> str:
    """Cria um administrador e retorna seu token."""
    auth_service = AuthServiceImpl()
    admin_id = uuid4()
    admin = UserModel(
        id=admin_id,
        email="admin@test.com",
        full_name="Admin User",
        hashed_password="hashed_password",
        user_type=UserType.ADMIN.value,
        is_active=True,
        is_verified=True
    )
    db_session.add(admin)
    await db_session.commit()
    
    return auth_service.create_access_token(user_id=admin_id, user_type=UserType.ADMIN)

@pytest.mark.asyncio
async def test_list_users_as_admin(client: AsyncClient, admin_token: str, db_session: AsyncSession):
    """Testa a listagem de usuários como administrador."""
    # Adicionar alguns usuários
    user1 = UserModel(
        id=uuid4(),
        email="user1@test.com",
        full_name="User One",
        hashed_password="hashed",
        user_type=UserType.STUDENT.value,
        is_active=True,
        is_verified=True
    )
    user2 = UserModel(
        id=uuid4(),
        email="user2@test.com",
        full_name="User Two",
        hashed_password="hashed",
        user_type=UserType.INSTRUCTOR.value,
        is_active=True,
        is_verified=True
    )
    db_session.add_all([user1, user2])
    await db_session.commit()

    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await client.get("/api/v1/admin/users", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert data["total_count"] >= 3  # Admin + 2 users
    assert any(u["email"] == "user1@test.com" for u in data["users"])
    assert any(u["email"] == "user2@test.com" for u in data["users"])

@pytest.mark.asyncio
async def test_search_users_as_admin(client: AsyncClient, admin_token: str, db_session: AsyncSession):
    """Testa a busca de usuários."""
    user = UserModel(
        id=uuid4(),
        email="searchable@test.com",
        full_name="Searchable User",
        hashed_password="hashed",
        user_type=UserType.STUDENT.value,
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    await db_session.commit()

    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await client.get("/api/v1/admin/users/search?q=Searchable", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["email"] == "searchable@test.com"

@pytest.mark.asyncio
async def test_toggle_user_status(client: AsyncClient, admin_token: str, db_session: AsyncSession):
    """Testa a alteração de status do usuário."""
    user = UserModel(
        id=uuid4(),
        email="toggle@test.com",
        full_name="Toggle User",
        hashed_password="hashed",
        user_type=UserType.STUDENT.value,
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    await db_session.commit()

    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Toggle to deactive
    response = await client.patch(f"/api/v1/admin/users/{user.id}/status", headers=headers)
    assert response.status_code == 200
    assert response.json()["is_active"] is False

    # Toggle back to active
    response = await client.patch(f"/api/v1/admin/users/{user.id}/status", headers=headers)
    assert response.status_code == 200
    assert response.json()["is_active"] is True

@pytest.mark.asyncio
async def test_admin_endpoints_require_admin(client: AsyncClient, db_session: AsyncSession):
    """Testa que usuários não-admin não podem acessar os endpoints."""
    auth_service = AuthServiceImpl()
    student_id = uuid4()
    student = UserModel(
        id=student_id,
        email="student@test.com",
        full_name="Student User",
        hashed_password="hashed",
        user_type=UserType.STUDENT.value,
        is_active=True,
        is_verified=True
    )
    db_session.add(student)
    await db_session.commit()
    
    token = auth_service.create_access_token(user_id=student_id, user_type=UserType.STUDENT)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = await client.get("/api/v1/admin/users", headers=headers)
    assert response.status_code == 403
