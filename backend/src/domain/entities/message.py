"""
Message Entity

Entidade de domínio representando uma mensagem de chat entre usuários.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class Message:
    """
    Entidade de mensagem de chat.

    Attributes:
        sender_id: ID do usuário que enviou a mensagem.
        receiver_id: ID do usuário que recebeu a mensagem.
        content: Conteúdo da mensagem.
        timestamp: Data e hora do envio.
        is_read: Indica se a mensagem foi lida pelo destinatário.
        id: Identificador único da mensagem.
    """

    sender_id: UUID
    receiver_id: UUID
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_read: bool = False
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        """Valida campos após inicialização."""
        if not self.content.strip():
            raise ValueError("Conteúdo da mensagem não pode estar vazio")
        if self.sender_id == self.receiver_id:
            raise ValueError("Remetente e destinatário devem ser diferentes")

    def mark_as_read(self) -> None:
        """Marca a mensagem como lida."""
        self.is_read = True
