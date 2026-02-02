"""
RefreshToken Entity

Entidade de domínio representando um token de refresh.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class RefreshToken:
    """
    Entidade de refresh token para autenticação.

    Usado para renovar access tokens sem necessidade de novo login.
    Implementa rotação obrigatória conforme PROJECT_GUIDELINES.md.
    """

    token_hash: str
    user_id: UUID
    expires_at: datetime
    id: UUID = field(default_factory=uuid4)
    is_revoked: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def revoke(self) -> None:
        """Revoga o token, tornando-o inválido."""
        self.is_revoked = True

    @property
    def is_expired(self) -> bool:
        """Verifica se o token expirou."""
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Verifica se o token é válido (não revogado e não expirado)."""
        return not self.is_revoked and not self.is_expired
