"""
OAuth Router — Mercado Pago

Endpoints para vinculação de conta Mercado Pago do instrutor via OAuth.
"""

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status

from fastapi.responses import HTMLResponse
from src.application.dtos.payment_dtos import (
    OAuthCallbackDTO,
    OAuthAuthorizeResponseDTO,
    OAuthCallbackResponseDTO,
)
from src.application.use_cases.payment.oauth_authorize_instructor import (
    OAuthAuthorizeInstructorUseCase,
)
from src.application.use_cases.payment.oauth_callback import OAuthCallbackUseCase
from src.domain.entities.user import User
from src.domain.exceptions import InstructorNotFoundException
from src.domain.interfaces.instructor_repository import IInstructorRepository
from src.domain.interfaces.payment_gateway import IPaymentGateway
from src.infrastructure.config import Settings, get_settings
from src.interface.api.dependencies import (
    CurrentInstructor,
    InstructorRepo,
    DBSession,
)

logger = structlog.get_logger()

router = APIRouter(prefix="/oauth/mercadopago", tags=["OAuth - Mercado Pago"])


# =============================================================================
# Dependencies locais para use cases OAuth
# =============================================================================


def _get_payment_gateway(
    settings: Settings = Depends(get_settings),
) -> IPaymentGateway:
    """Fornece instância do gateway Mercado Pago."""
    from src.infrastructure.external.mercadopago_gateway import MercadoPagoGateway
    return MercadoPagoGateway(settings)


def _get_authorize_use_case(
    instructor_repo: InstructorRepo,
    settings: Settings = Depends(get_settings),
) -> OAuthAuthorizeInstructorUseCase:
    return OAuthAuthorizeInstructorUseCase(instructor_repo, settings)


def _get_callback_use_case(
    instructor_repo: InstructorRepo,
    gateway: IPaymentGateway = Depends(_get_payment_gateway),
    settings: Settings = Depends(get_settings),
) -> OAuthCallbackUseCase:
    return OAuthCallbackUseCase(instructor_repo, gateway, settings)


# =============================================================================
# Endpoints
# =============================================================================


@router.get(
    "/authorize",
    response_model=None,
    summary="Gerar URL de autorização OAuth",
    description="Gera a URL para o instrutor vincular sua conta Mercado Pago.",
)
async def authorize(
    current_user: CurrentInstructor,
    use_case: OAuthAuthorizeInstructorUseCase = Depends(_get_authorize_use_case),
) -> dict:
    """
    Gera a URL de autorização OAuth do Mercado Pago.

    O instrutor deve abrir essa URL no browser para autorizar o GoDrive
    a acessar sua conta Mercado Pago para receber pagamentos.
    """
    try:
        result = await use_case.execute(current_user.id)
        return {
            "authorization_url": result.authorization_url,
            "state": result.state,
        }
    except InstructorNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de instrutor não encontrado",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/callback",
    response_model=None,
    summary="Callback OAuth do Mercado Pago",
    description="Endpoint chamado pelo Mercado Pago após autorização do instrutor.",
)
async def callback(
    code: str = Query(..., description="Código de autorização do MP"),
    state: str = Query(..., description="ID do instrutor (state parameter)"),
    use_case: OAuthCallbackUseCase = Depends(_get_callback_use_case),
    db_session: DBSession = None,
) -> HTMLResponse:
    """
    Processa o callback OAuth do Mercado Pago.

    Este endpoint é público (sem JWT) porque o Mercado Pago redireciona
    o browser do instrutor para cá. A segurança é garantida pelo
    parâmetro `state` que contém o ID do instrutor.
    """
    try:
        dto = OAuthCallbackDTO(code=code, state=state)
        result = await use_case.execute(dto)

        # Commit explícito necessário pois GET não faz auto-commit
        if db_session:
            await db_session.commit()

        logger.info(
            "oauth_callback_success",
            mp_user_id=result.mp_user_id,
            state=state,
        )

        html_content = """
        <html>
            <head>
                <title>Autorização Concluída</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; text-align: center; padding: 40px; }
                    h1 { color: #059669; }
                    p { color: #4B5563; font-size: 16px; margin-top: 20px; }
                </style>
            </head>
            <body>
                <h1>Autorização Concluída!</h1>
                <p>Sua conta Mercado Pago foi vinculada com sucesso.</p>
                <p>Você já pode fechar esta página e voltar para o aplicativo GoDrive.</p>
            </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    except InstructorNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instrutor não encontrado",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(
            "oauth_callback_error",
            error=str(e),
            state=state,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Erro ao processar autorização com Mercado Pago",
        )
