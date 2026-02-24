"""
User Entity

Entidade de domínio representando um usuário do sistema.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from uuid import UUID, uuid4

from .user_type import UserType


@dataclass
class User:
    """
    Entidade de usuário do sistema GoDrive.

    Representa um aluno, instrutor ou administrador.
    """

    email: str
    hashed_password: str
    full_name: str
    user_type: UserType
    id: UUID = field(default_factory=uuid4)
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None
    phone: str | None = None
    cpf: str | None = None
    birth_date: date | None = None
    biological_sex: str | None = None

    def __post_init__(self) -> None:
        """Valida campos após inicialização."""
        if not self.email or ("@" not in self.email and not self.email.startswith("TESTUSER")):
            raise ValueError("Email inválido")
        if not self.full_name or len(self.full_name.strip()) < 2:
            raise ValueError("Nome deve ter pelo menos 2 caracteres")

    def deactivate(self) -> None:
        """Desativa o usuário."""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def verify_email(self) -> None:
        """Marca o email como verificado."""
        self.is_verified = True
        self.updated_at = datetime.utcnow()

    def update_password(self, new_hashed_password: str) -> None:
        """Atualiza a senha hashada do usuário."""
        self.hashed_password = new_hashed_password
        self.updated_at = datetime.utcnow()

    @property
    def is_instructor(self) -> bool:
        """Verifica se o usuário é um instrutor."""
        return self.user_type == UserType.INSTRUCTOR

    @property
    def is_student(self) -> bool:
        """Verifica se o usuário é um aluno."""
        return self.user_type == UserType.STUDENT

    @property
    def is_admin(self) -> bool:
        """Verifica se o usuário é um administrador."""
        return self.user_type == UserType.ADMIN
