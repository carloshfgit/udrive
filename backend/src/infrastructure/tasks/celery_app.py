"""
Celery App Configuration

Define o aplicativo Celery e o agendamento de tarefas periódicas (Celery Beat).
"""

from celery import Celery
from celery.schedules import crontab

# Configuração do Celery
# Broker: Redis (db 0)
# Backend: Redis (db 1)
celery_app = Celery(
    "godrive",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1",
    include=["src.infrastructure.tasks.payment_tasks"],
)

celery_app.conf.update(
    timezone="UTC",
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # Agendamento de tarefas do Celery Beat
    beat_schedule={
        "expire-stale-reservations": {
            "task": "src.infrastructure.tasks.payment_tasks.expire_stale_reservations",
            "schedule": 60.0,  # a cada 60 segundos
        },
        "auto-confirm-completed-lessons": {
            "task": "src.infrastructure.tasks.payment_tasks.auto_confirm_completed_lessons",
            "schedule": crontab(minute=0),  # a cada hora
        },
    },
)

# As tarefas são carregadas via o argumento 'include' no construtor do Celery acima.
