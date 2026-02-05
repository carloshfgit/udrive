from starlette.requests import Request
from starlette.responses import RedirectResponse
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select

from src.infrastructure.db.database import AsyncSessionLocal
from src.infrastructure.db.models.user_model import UserModel
from src.infrastructure.services.auth_service_impl import AuthServiceImpl
from src.domain.entities.user_type import UserType


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form["username"], form["password"]

        auth_service = AuthServiceImpl()

        async with AsyncSessionLocal() as session:
            stmt = select(UserModel).where(UserModel.email == email)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                return False

            if not auth_service.verify_password(password, user.hashed_password):
                return False

            if user.user_type != UserType.ADMIN.value:
                # Opcional: permitir verificação mesmo se login correto, 
                # mas política diz restrito a ADMIN.
                return False

        # Session is implemented via SessionMiddleware in main.py
        request.session.update({"user_id": str(user.id)})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        user_id = request.session.get("user_id")
        return bool(user_id)
