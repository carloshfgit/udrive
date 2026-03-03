"""
Celery Application Configuration

Configura o Celery com Redis como broker e backend de resultados.
As tasks são auto-descobertas a partir do pacote infrastructure.tasks.
"""

from celery import Celery

from src.infrastructure.config import settings

# Criar app Celery com broker Redis
celery_app = Celery(
    "godrive",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

# Configurações
celery_app.conf.update(
    # Serialização
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # Timezone
    timezone="UTC",
    enable_utc=True,
    # Retry
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # Resultados expiram após 1 hora
    result_expires=3600,
    # Worker
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Registrar tasks explicitamente
# (autodiscover busca 'tasks.py' por padrão;
#  usamos include para nosso 'notification_tasks.py' e 'cart_tasks.py')
celery_app.conf.include = [
    "src.infrastructure.tasks.notification_tasks",
    "src.infrastructure.tasks.cart_tasks",
]

# Configurar o Celery Beat para rodar as tarefas periodicamente
celery_app.conf.beat_schedule = {
    "cleanup-expired-carts-every-2-minutes": {
        "task": "cart.cleanup_expired_items",
        "schedule": 120.0,  # A cada 120 segundos (2 minutos)
    },
}
