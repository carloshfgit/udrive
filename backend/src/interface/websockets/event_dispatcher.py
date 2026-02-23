"""
Scheduling Event Dispatcher

Emite eventos de agendamento via Redis PubSub para notificar
a outra parte em tempo real (instrutor ou aluno).

Mantém Clean Architecture: os use cases não são modificados.
Os routers chamam o dispatcher após execução bem-sucedida do use case.
"""

from uuid import UUID

import structlog

from src.application.dtos.scheduling_dtos import SchedulingResponseDTO
from src.infrastructure.external.redis_pubsub import RedisPubSubService
from src.interface.websockets.message_types import SchedulingEventType

logger = structlog.get_logger()


class SchedulingEventDispatcher:
    """
    Emite eventos de agendamento via Redis PubSub para o outro participante.

    Cada método serializa o DTO e publica no canal pessoal do destinatário.
    Se o Redis estiver offline, o erro é logado mas não impede o fluxo REST.
    """

    def __init__(self, pubsub_service: RedisPubSubService) -> None:
        self._pubsub = pubsub_service

    def _serialize(self, dto: SchedulingResponseDTO) -> dict:
        """Serializa o DTO de agendamento para dict JSON-compatible."""
        return {
            "id": str(dto.id),
            "student_id": str(dto.student_id),
            "instructor_id": str(dto.instructor_id),
            "scheduled_datetime": str(dto.scheduled_datetime),
            "duration_minutes": dto.duration_minutes,
            "price": str(dto.price),
            "status": dto.status,
            "cancellation_reason": dto.cancellation_reason,
            "cancelled_by": str(dto.cancelled_by) if dto.cancelled_by else None,
            "cancelled_at": str(dto.cancelled_at) if dto.cancelled_at else None,
            "completed_at": str(dto.completed_at) if dto.completed_at else None,
            "started_at": str(dto.started_at) if dto.started_at else None,
            "rescheduled_datetime": str(dto.rescheduled_datetime) if dto.rescheduled_datetime else None,
            "rescheduled_by": str(dto.rescheduled_by) if dto.rescheduled_by else None,
            "created_at": str(dto.created_at) if dto.created_at else None,
            "student_name": dto.student_name,
            "instructor_name": dto.instructor_name,
        }

    async def _safe_publish(self, channel: str, data: dict) -> None:
        """Publica com tratamento de erro — falha não impede o fluxo REST."""
        try:
            await self._pubsub.publish(channel, data)
        except Exception as e:
            logger.error(
                "event_dispatcher_publish_error",
                channel=channel,
                event_type=data.get("type"),
                error=str(e),
            )

    async def emit_scheduling_created(self, dto: SchedulingResponseDTO) -> None:
        """Notifica o INSTRUTOR que recebeu novo agendamento."""
        await self._safe_publish(
            f"user:{dto.instructor_id}",
            {"type": SchedulingEventType.SCHEDULING_CREATED, "data": self._serialize(dto)},
        )
        logger.info(
            "scheduling_event_emitted",
            event_type=SchedulingEventType.SCHEDULING_CREATED,
            target="instructor",
            scheduling_id=str(dto.id),
        )

    async def emit_scheduling_confirmed(self, dto: SchedulingResponseDTO) -> None:
        """Notifica o ALUNO que o agendamento foi confirmado."""
        await self._safe_publish(
            f"user:{dto.student_id}",
            {"type": SchedulingEventType.SCHEDULING_CONFIRMED, "data": self._serialize(dto)},
        )
        logger.info(
            "scheduling_event_emitted",
            event_type=SchedulingEventType.SCHEDULING_CONFIRMED,
            target="student",
            scheduling_id=str(dto.id),
        )

    async def emit_scheduling_cancelled(
        self, dto: SchedulingResponseDTO, cancelled_by: UUID
    ) -> None:
        """Notifica a OUTRA PARTE que o agendamento foi cancelado."""
        target_id = dto.student_id if cancelled_by == dto.instructor_id else dto.instructor_id
        await self._safe_publish(
            f"user:{target_id}",
            {"type": SchedulingEventType.SCHEDULING_CANCELLED, "data": self._serialize(dto)},
        )
        logger.info(
            "scheduling_event_emitted",
            event_type=SchedulingEventType.SCHEDULING_CANCELLED,
            target=str(target_id),
            scheduling_id=str(dto.id),
        )

    async def emit_scheduling_started(
        self, dto: SchedulingResponseDTO, started_by: UUID
    ) -> None:
        """Notifica a OUTRA PARTE que a aula começou."""
        target_id = dto.student_id if started_by != dto.student_id else dto.instructor_id
        await self._safe_publish(
            f"user:{target_id}",
            {"type": SchedulingEventType.SCHEDULING_STARTED, "data": self._serialize(dto)},
        )
        logger.info(
            "scheduling_event_emitted",
            event_type=SchedulingEventType.SCHEDULING_STARTED,
            target=str(target_id),
            scheduling_id=str(dto.id),
        )

    async def emit_scheduling_completed(self, dto: SchedulingResponseDTO) -> None:
        """Notifica AMBAS as partes que a aula foi concluída."""
        data = {"type": SchedulingEventType.SCHEDULING_COMPLETED, "data": self._serialize(dto)}
        await self._safe_publish(f"user:{dto.student_id}", data)
        await self._safe_publish(f"user:{dto.instructor_id}", data)
        logger.info(
            "scheduling_event_emitted",
            event_type=SchedulingEventType.SCHEDULING_COMPLETED,
            target="both",
            scheduling_id=str(dto.id),
        )

    async def emit_reschedule_requested(self, dto: SchedulingResponseDTO) -> None:
        """Notifica o OUTRO participante que recebeu solicitação de reagendamento."""
        target_id = dto.instructor_id if dto.rescheduled_by == dto.student_id else dto.student_id
        await self._safe_publish(
            f"user:{target_id}",
            {"type": SchedulingEventType.RESCHEDULE_REQUESTED, "data": self._serialize(dto)},
        )
        logger.info(
            "scheduling_event_emitted",
            event_type=SchedulingEventType.RESCHEDULE_REQUESTED,
            target=str(target_id),
            scheduling_id=str(dto.id),
        )

    async def emit_reschedule_responded(
        self, dto: SchedulingResponseDTO, accepted: bool
    ) -> None:
        """Notifica o participante que SOLICITOU sobre a resposta do reagendamento."""
        # Se o reagendamento foi aceito/recusado, enviamos para quem tinha solicitado originalmente.
        # Notar que após accept/refuse, a entidade limpa rescheduled_by, 
        # mas o DTO de resposta contém o estado ANTERIOR ou o dispatcher recebe o DTO processado.
        # Se o DTO processado tem rescheduled_by=None (como está na entidade), 
        # precisamos que o DTO ainda tenha esse dado ou passá-lo explicitamente.
        
        # Vamos conferir o RespondRescheduleUseCase... ele retorna SchedulingResponseDTO.
        # Na entidade accept_reschedule() limpa rescheduled_by. 
        # Então no DTO 'result' ele será None.
        
        # OPA! Problema detectado. Se o use case retorna a entidade salva, 
        # o rescheduled_by já foi limpo.
        
        # Precisamos notificar a parte que NÃO é a que está respondendo.
        # Como o dispatcher é chamado pelo router que sabe quem é o current_user,
        # mas aqui no método só recebemos o DTO.
        
        # Se dto.rescheduled_by é None, enviamos para AMBOS para garantir, 
        # ou mudamos a assinatura para receber o responder_id.
        
        # No entanto, se o objetivo é tempo real, o responder_id é o current_user.
        # O outro participante é:
        # target_id = student if responder == instructor else instructor
        
        # Mas não temos o responder_id aqui.
        # Vamos assumir que se dto.rescheduled_by é None (comum após resposta),
        # enviamos para ambos ou tentamos inferir.
        
        # O mais seguro é enviar para ambos se não soubermos quem é o alvo,
        # ou confiar que o front-end filtra o que é dele.
        
        payload = {**self._serialize(dto), "accepted": accepted}
        await self._safe_publish(f"user:{dto.student_id}", {"type": SchedulingEventType.RESCHEDULE_RESPONDED, "data": payload})
        await self._safe_publish(f"user:{dto.instructor_id}", {"type": SchedulingEventType.RESCHEDULE_RESPONDED, "data": payload})
        
        logger.info(
            "scheduling_event_emitted",
            event_type=SchedulingEventType.RESCHEDULE_RESPONDED,
            target="both",
            accepted=accepted,
            scheduling_id=str(dto.id),
        )


# Instância global (inicializada no startup com pubsub_service)
_event_dispatcher: SchedulingEventDispatcher | None = None


def get_event_dispatcher() -> SchedulingEventDispatcher | None:
    """Retorna a instância global do event dispatcher."""
    return _event_dispatcher


def init_event_dispatcher(pubsub_service: RedisPubSubService) -> SchedulingEventDispatcher:
    """Inicializa o event dispatcher global com o serviço PubSub."""
    global _event_dispatcher
    _event_dispatcher = SchedulingEventDispatcher(pubsub_service)
    logger.info("event_dispatcher_initialized")
    return _event_dispatcher
