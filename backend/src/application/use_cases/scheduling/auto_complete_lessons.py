"""
Auto Complete Lessons Use Case

Caso de uso para marcar aulas como concluídas automaticamente
quando o aluno não confirma dentro de 24h após o término.
"""

import logging
from dataclasses import dataclass

from src.domain.interfaces.scheduling_repository import ISchedulingRepository

logger = logging.getLogger(__name__)


@dataclass
class AutoCompleteLessonsUseCase:
    """
    Caso de uso para auto-completar aulas pendentes de confirmação.

    Regra (PAYMENT_FLOW.md):
        Se o aluno não confirmar a conclusão em 24h após o término
        da aula, o sistema marca automaticamente como concluída.

    Fluxo:
        1. Buscar agendamentos CONFIRMED cuja aula terminou há > 24h
        2. Para cada um: student_confirm_completion() + complete()
        3. Persistir alterações
        4. Retornar contagem de aulas auto-completadas
    """

    scheduling_repository: ISchedulingRepository

    async def execute(self, hours_threshold: int = 24) -> int:
        """
        Executa auto-completar para aulas atrasadas.

        Args:
            hours_threshold: Horas após o término da aula (default 24).

        Returns:
            Número de aulas auto-completadas.
        """
        overdue_schedulings = await self.scheduling_repository.get_overdue_confirmed(
            hours_threshold=hours_threshold
        )

        if not overdue_schedulings:
            logger.info("Nenhuma aula pendente de auto-confirmação encontrada.")
            return 0

        completed_count = 0
        for scheduling in overdue_schedulings:
            try:
                scheduling.student_confirm_completion()
                scheduling.complete()
                await self.scheduling_repository.update(scheduling)
                completed_count += 1
                logger.info(
                    f"Aula {scheduling.id} auto-completada com sucesso."
                )
            except Exception as e:
                logger.error(
                    f"Erro ao auto-completar aula {scheduling.id}: {e}"
                )
                # Continua processando as demais aulas

        logger.info(
            f"Auto-complete finalizado: {completed_count}/{len(overdue_schedulings)} aulas processadas."
        )
        return completed_count
