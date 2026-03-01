"""
Infrastructure - Tasks

Tarefas assíncronas com Celery para processamento em background.
Inclui tarefas de notificação: lembretes de aula e solicitação de avaliação.
"""

from src.infrastructure.tasks.celery_app import celery_app

__all__ = ["celery_app"]
