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
    DisputeAdmin,
)


import os

def setup_admin(app: FastAPI, engine: AsyncEngine) -> None:
    """Configura a interface administrativa."""
    
    authentication_backend = AdminAuth(secret_key=settings.jwt_secret_key)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(base_dir, "templates")

    admin = Admin(
        app=app,
        engine=engine,
        authentication_backend=authentication_backend,
        title="GoDrive Admin",
        templates_dir=templates_dir,
    )

    admin.add_view(UserAdmin)
    admin.add_view(InstructorProfileAdmin)
    admin.add_view(StudentProfileAdmin)
    admin.add_view(SchedulingAdmin)
    admin.add_view(DisputeAdmin)
