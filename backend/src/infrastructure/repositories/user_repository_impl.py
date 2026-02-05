"""
User Repository Implementation

Implementação concreta do repositório de usuários usando SQLAlchemy.
"""

from uuid import UUID

from sqlalchemy import select
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
                    UserModel.hashed_password,
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
        stmt = select(UserModel).where(UserModel.email == email.lower())
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
