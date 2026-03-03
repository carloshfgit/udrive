"""
Auto Complete Lessons Use Case

Caso de uso para marcar aulas como concluídas automaticamente
quando o aluno não confirma dentro de 24h após o término.
"""

import structlog
from dataclasses import dataclass

from src.domain.interfaces.scheduling_repository import ISchedulingRepository

logger = structlog.get_logger(__name__)


@dataclass
class AutoCompleteLessonsUseCase:
    """
    Caso de uso para auto-completar aulas pendentes de confirmação.

    Regra:
        Se o aluno não confirmar a conclusão em 24h após o término
        da aula, o sistema marca automaticamente como concluída.
        Aulas com status DISPUTED são ignoradas.

    Fluxo:
        1. Buscar agendamentos CONFIRMED cuja aula terminou há > 24h
        2. Para cada um: auto_complete() (não exige started_at/student_confirmed_at)
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
            logger.info("auto_complete_no_overdue_found")
            return 0

        completed_count = 0
        for scheduling in overdue_schedulings:
            try:
                scheduling.auto_complete()
                await self.scheduling_repository.update(scheduling)
                completed_count += 1
                logger.info(
                    "auto_complete_lesson_success",
                    scheduling_id=str(scheduling.id),
                )
            except Exception as e:
                logger.error(
                    "auto_complete_lesson_error",
                    scheduling_id=str(scheduling.id),
                    error=str(e),
                )

        logger.info(
            "auto_complete_finished",
            completed=completed_count,
            total=len(overdue_schedulings),
        )
        return completed_count
