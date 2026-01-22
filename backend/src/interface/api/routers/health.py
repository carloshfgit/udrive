"""
Health Check Router

Endpoints para verificação de saúde da aplicação.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """
    Verifica se a aplicação está funcionando.

    Returns:
        dict: Status da aplicação.
    """
    return {"status": "healthy", "service": "godrive-api"}


@router.get("/health/ready")
async def readiness_check() -> dict[str, str]:
    """
    Verifica se a aplicação está pronta para receber requisições.

    Útil para Kubernetes readiness probes.

    Returns:
        dict: Status de prontidão.
    """
    # TODO: Adicionar verificação de conexão com DB e Redis
    return {"status": "ready"}
