"""
CreateReviewUseCase

Caso de uso para criação de avaliação de aula.
"""

from uuid import UUID

from src.domain.entities.review import Review
from src.domain.entities.scheduling_status import SchedulingStatus
from src.domain.interfaces.instructor_repository import IInstructorRepository
from src.domain.interfaces.review_repository import IReviewRepository
from src.domain.interfaces.scheduling_repository import ISchedulingRepository


class CreateReviewUseCase:
    """
    Coordina a criação de uma nova avaliação de aula.
    """

    def __init__(
        self,
        review_repo: IReviewRepository,
        scheduling_repo: ISchedulingRepository,
        instructor_repo: IInstructorRepository,
    ) -> None:
        self._review_repo = review_repo
        self._scheduling_repo = scheduling_repo
        self._instructor_repo = instructor_repo

    async def execute(
        self,
        scheduling_id: UUID,
        student_id: UUID,
        rating: int,
        comment: str | None = None,
    ) -> Review:
        """
        Executa o processo de avaliação.

        Args:
            scheduling_id: ID do agendamento.
            student_id: ID do aluno avaliador.
            rating: Nota (1-5).
            comment: Comentário opcional.

        Returns:
            Review criado.

        Raises:
            ValueError: Se o agendamento não for encontrado, não estiver concluído,
                       já possuir avaliação ou se o aluno for diferente.
        """
        # 1. Buscar agendamento
        scheduling = await self._scheduling_repo.get_by_id(scheduling_id)
        if scheduling is None:
            raise ValueError("Agendamento não encontrado")

        # 2. Validar permissão (aluno dono do agendamento)
        if scheduling.student_id != student_id:
            raise ValueError("Apenas o aluno que realizou o agendamento pode avaliá-lo")

        # 3. Validar status (apenas concluídos)
        if scheduling.status != SchedulingStatus.COMPLETED:
            raise ValueError(
                f"Apenas aulas concluídas podem ser avaliadas. Status atual: {scheduling.status}"
            )

        # 4. Verificar se já existe avaliação
        existing_review = await self._review_repo.get_by_scheduling_id(scheduling_id)
        if existing_review:
            raise ValueError("Este agendamento já foi avaliado")

        # 5. Buscar perfil do instrutor
        instructor_profile = await self._instructor_repo.get_by_user_id(
            scheduling.instructor_id
        )
        if instructor_profile is None:
            raise ValueError("Perfil do instrutor não encontrado")

        # 6. Criar entidade de avaliação
        review = Review(
            scheduling_id=scheduling_id,
            student_id=student_id,
            instructor_id=scheduling.instructor_id,
            rating=rating,
            comment=comment,
        )

        # 7. Atualizar perfil do instrutor (rating e total_reviews)
        instructor_profile.add_review(float(rating))

        # 8. Persistir as mudanças
        saved_review = await self._review_repo.create(review)
        await self._instructor_repo.update(instructor_profile)

        return saved_review
