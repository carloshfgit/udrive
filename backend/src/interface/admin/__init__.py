from fastapi import FastAPI
from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncEngine

from src.infrastructure.config import settings
from src.interface.admin.auth import AdminAuth
from src.interface.admin.views import (
    InstructorProfileAdmin,
    SchedulingAdmin,
    StudentProfileAdmin,
    UserAdmin,
)


def setup_admin(app: FastAPI, engine: AsyncEngine) -> None:
    """Configura a interface administrativa."""
    
    authentication_backend = AdminAuth(secret_key=settings.jwt_secret_key)

    admin = Admin(
        app=app,
        engine=engine,
        authentication_backend=authentication_backend,
        title="GoDrive Admin",
    )

    admin.add_view(UserAdmin)
    admin.add_view(InstructorProfileAdmin)
    admin.add_view(StudentProfileAdmin)
    admin.add_view(SchedulingAdmin)
