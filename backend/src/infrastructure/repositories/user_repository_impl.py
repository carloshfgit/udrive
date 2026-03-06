"""
User Repository Implementation

Implementação concreta do repositório de usuários usando SQLAlchemy.
"""

from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import load_only
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.infrastructure.db.models.user_model import UserModel


class UserRepositoryImpl:
    """
    Implementação do repositório de usuários.

    Usa SQLAlchemy 2.0+ com sintaxe moderna select().
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Inicializa o repositório.

        Args:
            session: Sessão assíncrona do SQLAlchemy.
        """
        self._session = session

    async def create(self, user: User) -> User:
        """
        Cria um novo usuário.

        Args:
            user: Entidade de usuário a ser criada.

        Returns:
            User: Usuário criado.
        """
        model = UserModel.from_entity(user)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model.to_entity()

    async def get_by_id(self, user_id: UUID) -> User | None:
        """
        Busca usuário por ID.

        Args:
            user_id: UUID do usuário.

        Returns:
            User | None: Usuário encontrado ou None.
        """
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_essential_by_id(self, user_id: UUID) -> User | None:
        """
        Busca apenas campos essenciais do usuário por ID (sem senha).
        """
        stmt = (
            select(UserModel)
            .where(UserModel.id == user_id)
            .options(
                load_only(
                    UserModel.id,
                    UserModel.email,
                    UserModel.full_name,
                    UserModel.user_type,
                    UserModel.is_active,
                    UserModel.is_verified,
                    UserModel.phone,
                    UserModel.cpf,
                    UserModel.birth_date,
                    UserModel.biological_sex,
                    UserModel.created_at,
                    UserModel.updated_at,
                )
            )
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_email(self, email: str) -> User | None:
        """
        Busca usuário por email.

        Args:
            email: Email do usuário.

        Returns:
            User | None: Usuário encontrado ou None.
        """
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def update(self, user: User) -> User:
        """
        Atualiza um usuário existente.

        Args:
            user: Entidade de usuário com dados atualizados.

        Returns:
            User: Usuário atualizado.
        """
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            raise ValueError(f"Usuário não encontrado: {user.id}")

        # Atualizar campos
        model.email = user.email
        model.hashed_password = user.hashed_password
        model.full_name = user.full_name
        model.user_type = user.user_type.value
        model.is_active = user.is_active
        model.is_verified = user.is_verified
        model.phone = user.phone
        model.cpf = user.cpf
        model.birth_date = user.birth_date
        model.biological_sex = user.biological_sex

        await self._session.flush()
        await self._session.refresh(model)
        return model.to_entity()

    async def delete(self, user_id: UUID) -> bool:
        """
        Remove um usuário.

        Args:
            user_id: UUID do usuário a remover.

        Returns:
            bool: True se removido, False se não encontrado.
        """
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return False

        await self._session.delete(model)
        await self._session.flush()
        return True

    async def list_all(
        self,
        user_type: str | None = None,
        is_active: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[User]:
        """
        Lista todos os usuários com filtros opcionais.
        """
        stmt = select(UserModel)

        if user_type is not None:
            stmt = stmt.where(UserModel.user_type == user_type)
        if is_active is not None:
            stmt = stmt.where(UserModel.is_active == is_active)

        stmt = stmt.order_by(UserModel.created_at.desc())
        stmt = stmt.limit(limit).offset(offset)

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [m.to_entity() for m in models]

    async def count_all(
        self,
        user_type: str | None = None,
        is_active: bool | None = None,
    ) -> int:
        """
        Conta usuários com filtros opcionais.
        """
        stmt = select(func.count()).select_from(UserModel)

        if user_type is not None:
            stmt = stmt.where(UserModel.user_type == user_type)
        if is_active is not None:
            stmt = stmt.where(UserModel.is_active == is_active)

        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def search(
        self, query: str, limit: int = 20
    ) -> list[User]:
        """
        Busca usuários por nome, email ou CPF (ILIKE).
        """
        pattern = f"%{query}%"
        stmt = (
            select(UserModel)
            .where(
                or_(
                    UserModel.full_name.ilike(pattern),
                    UserModel.email.ilike(pattern),
                    UserModel.cpf.ilike(pattern),
                )
            )
            .order_by(UserModel.full_name)
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [m.to_entity() for m in models]

