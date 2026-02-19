"""
Clear Student Cart Use Case

Caso de uso para cancelar todos os agendamentos expirados ou pendentes no carrinho de um aluno.
"""

import structlog
from dataclasses import dataclass
from uuid import UUID

from src.domain.interfaces.scheduling_repository import ISchedulingRepository
from src.domain.interfaces.user_repository import IUserRepository

logger = structlog.get_logger()

@dataclass
class ClearStudentCartUseCase:
    """
    Caso de uso para limpar o carrinho de um aluno.
    
    Cancela todos os agendamentos que estão no carrinho (PENDING ou CONFIRMED sem pagamento).
    """

    scheduling_repository: ISchedulingRepository
    user_repository: IUserRepository

    async def execute(self, student_id: UUID) -> int:
        """
        Executa a limpeza do carrinho do aluno.

        Args:
            student_id: ID do aluno.

        Returns:
            int: Quantidade de agendamentos cancelados com sucesso.
        
        Nota: o endpoint HTTP que chama este use case é responsável
        pelo commit da transação. Falhas individuais são logadas mas
        não impedem o cancelamento dos demais itens.
        """
        expired_items = await self.scheduling_repository.get_expired_cart_items(
            student_id=student_id,
            timeout_minutes=0
        )

        if not expired_items:
            return 0

        cancelled_count = 0
        errors = []
        for scheduling in expired_items:
            try:
                scheduling.cancel(
                    cancelled_by=student_id,
                    reason="Carrinho expirado ou limpo pelo aluno"
                )
                await self.scheduling_repository.update(scheduling)
                cancelled_count += 1
                
                logger.info(
                    "cart_item_cleared",
                    scheduling_id=str(scheduling.id),
                    student_id=str(student_id)
                )
            except Exception as e:
                errors.append(str(scheduling.id))
                logger.error(
                    "clear_cart_item_error",
                    scheduling_id=str(scheduling.id),
                    error=str(e)
                )

        if errors:
            logger.warning(
                "clear_cart_partial_failure",
                student_id=str(student_id),
                total_items=len(expired_items),
                cancelled=cancelled_count,
                failed_ids=errors,
            )

        return cancelled_count
