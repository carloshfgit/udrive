"""
Testes unitários para Use Cases OAuth do Mercado Pago.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.application.dtos.payment_dtos import OAuthCallbackDTO
from src.application.use_cases.payment.oauth_authorize_instructor import (
    OAuthAuthorizeInstructorUseCase,
)
from src.application.use_cases.payment.oauth_callback import OAuthCallbackUseCase
from src.application.use_cases.payment.refresh_instructor_token import (
    RefreshInstructorTokenUseCase,
)
from src.domain.entities.instructor_profile import InstructorProfile
from src.domain.exceptions import InstructorNotFoundException
from src.domain.interfaces.payment_gateway import OAuthResult


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_instructor_repo():
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_payment_gateway():
    gateway = AsyncMock()
    return gateway


@pytest.fixture
def mock_settings():
    settings = MagicMock()
    settings.mp_client_id = "TEST_CLIENT_ID"
    settings.mp_client_secret = "TEST_CLIENT_SECRET"
    settings.mp_redirect_uri = "https://godrive.com/api/v1/oauth/mercadopago/callback"
    settings.encryption_key = "test-encryption-key-for-tests-only"
    return settings


@pytest.fixture
def instructor_profile():
    return InstructorProfile(
        user_id=uuid4(),
        bio="Instrutor de teste",
        vehicle_type="Hatch",
        license_category="B",
        hourly_rate=Decimal("80.00"),
        mp_access_token=None,
        mp_refresh_token=None,
        mp_token_expiry=None,
        mp_user_id=None,
    )


@pytest.fixture
def connected_instructor_profile():
    return InstructorProfile(
        user_id=uuid4(),
        bio="Instrutor conectado",
        vehicle_type="Sedan",
        license_category="B",
        hourly_rate=Decimal("100.00"),
        mp_access_token="encrypted_access_token",
        mp_refresh_token="encrypted_refresh_token",
        mp_token_expiry=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=90),
        mp_user_id="12345678",
    )


@pytest.fixture
def oauth_result():
    return OAuthResult(
        access_token="APP_USR-test-access-token",
        refresh_token="TG-test-refresh-token",
        expires_in=15552000,  # ~180 dias
        user_id="12345678",
        scope="read write offline_access",
    )


# =============================================================================
# OAuthAuthorizeInstructorUseCase
# =============================================================================


class TestOAuthAuthorizeInstructorUseCase:
    """Testes para geração de URL de autorização OAuth."""

    @pytest.mark.asyncio
    async def test_authorize_generates_correct_url(
        self, mock_instructor_repo, mock_settings, instructor_profile
    ):
        """Deve gerar URL OAuth com parâmetros corretos."""
        mock_instructor_repo.get_by_user_id.return_value = instructor_profile

        use_case = OAuthAuthorizeInstructorUseCase(
            mock_instructor_repo, mock_settings
        )
        result = await use_case.execute(instructor_profile.user_id)

        assert "auth.mercadopago.com/authorization" in result.authorization_url
        assert "TEST_CLIENT_ID" in result.authorization_url
        
        # O state não é mais o UUID puro, agora é JSON Base64
        assert result.state != str(instructor_profile.user_id)
        assert result.state in result.authorization_url
        
        # Opcional: validar conteúdo do state
        import base64
        import json
        padding = len(result.state) % 4
        decoded = base64.urlsafe_b64decode(result.state + ("=" * (4 - padding) if padding else "")).decode()
        data = json.loads(decoded)
        assert data["u"] == str(instructor_profile.user_id)

    @pytest.mark.asyncio
    async def test_authorize_instructor_not_found_raises(
        self, mock_instructor_repo, mock_settings
    ):
        """Deve lançar exceção se instrutor não for encontrado."""
        mock_instructor_repo.get_by_user_id.return_value = None

        use_case = OAuthAuthorizeInstructorUseCase(
            mock_instructor_repo, mock_settings
        )

        with pytest.raises(InstructorNotFoundException):
            await use_case.execute(uuid4())

    @pytest.mark.asyncio
    async def test_authorize_already_connected_raises(
        self, mock_instructor_repo, mock_settings, connected_instructor_profile
    ):
        """Deve lançar erro se instrutor já tiver conta MP vinculada."""
        mock_instructor_repo.get_by_user_id.return_value = connected_instructor_profile

        use_case = OAuthAuthorizeInstructorUseCase(
            mock_instructor_repo, mock_settings
        )

        with pytest.raises(ValueError, match="já possui conta Mercado Pago"):
            await use_case.execute(connected_instructor_profile.user_id)


# =============================================================================
# OAuthCallbackUseCase
# =============================================================================


class TestOAuthCallbackUseCase:
    """Testes para processamento do callback OAuth."""

    @pytest.mark.asyncio
    @patch("src.application.use_cases.payment.oauth_callback.encrypt_token")
    async def test_callback_saves_tokens(
        self,
        mock_encrypt,
        mock_instructor_repo,
        mock_payment_gateway,
        mock_settings,
        instructor_profile,
        oauth_result,
    ):
        """Deve trocar code por tokens e salvar no perfil do instrutor."""
        mock_encrypt.side_effect = lambda t: f"encrypted_{t}"
        mock_instructor_repo.get_by_user_id.return_value = instructor_profile
        mock_payment_gateway.authorize_seller.return_value = oauth_result

        use_case = OAuthCallbackUseCase(
            mock_instructor_repo, mock_payment_gateway, mock_settings
        )

        dto = OAuthCallbackDTO(
            code="TG-test-authorization-code",
            state=str(instructor_profile.user_id),
        )
        result = await use_case.execute(dto)

        # Verificar resultado
        assert result.mp_user_id == "12345678"
        assert result.is_connected is True

        # Verificar que o gateway foi chamado
        mock_payment_gateway.authorize_seller.assert_called_once_with(
            authorization_code="TG-test-authorization-code",
            redirect_uri=mock_settings.mp_redirect_uri,
        )

        # Verificar que o repositório salvou
        mock_instructor_repo.update.assert_called_once()
        saved_profile = mock_instructor_repo.update.call_args[0][0]
        assert saved_profile.mp_user_id == "12345678"
        assert saved_profile.mp_access_token == "encrypted_APP_USR-test-access-token"
        assert saved_profile.mp_refresh_token == "encrypted_TG-test-refresh-token"
        assert saved_profile.mp_token_expiry is not None

    @pytest.mark.asyncio
    async def test_callback_invalid_state_raises(
        self, mock_instructor_repo, mock_payment_gateway, mock_settings
    ):
        """Deve lançar exceção se state for inválido (não UUID)."""
        use_case = OAuthCallbackUseCase(
            mock_instructor_repo, mock_payment_gateway, mock_settings
        )

        dto = OAuthCallbackDTO(code="TG-code", state="invalid-not-a-uuid")

        with pytest.raises(ValueError, match="State inválido"):
            await use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_callback_instructor_not_found_raises(
        self, mock_instructor_repo, mock_payment_gateway, mock_settings
    ):
        """Deve lançar exceção se instrutor do state não existir."""
        mock_instructor_repo.get_by_user_id.return_value = None

        use_case = OAuthCallbackUseCase(
            mock_instructor_repo, mock_payment_gateway, mock_settings
        )

        dto = OAuthCallbackDTO(code="TG-code", state=str(uuid4()))

        with pytest.raises(InstructorNotFoundException):
            await use_case.execute(dto)


# =============================================================================
# RefreshInstructorTokenUseCase
# =============================================================================


class TestRefreshInstructorTokenUseCase:
    """Testes para renovação de tokens OAuth."""

    @pytest.mark.asyncio
    @patch("src.application.use_cases.payment.refresh_instructor_token.encrypt_token")
    @patch("src.application.use_cases.payment.refresh_instructor_token.decrypt_token")
    async def test_refresh_updates_tokens(
        self,
        mock_decrypt,
        mock_encrypt,
        mock_instructor_repo,
        mock_payment_gateway,
        connected_instructor_profile,
        oauth_result,
    ):
        """Deve renovar tokens quando próximos de expirar."""
        # Token expirando em 10 dias (abaixo do threshold de 30)
        connected_instructor_profile.mp_token_expiry = datetime.now(
            timezone.utc
        ).replace(tzinfo=None) + timedelta(days=10)

        mock_decrypt.return_value = "decrypted_refresh_token"
        mock_encrypt.side_effect = lambda t: f"new_encrypted_{t}"
        mock_instructor_repo.get_by_user_id.return_value = connected_instructor_profile
        mock_payment_gateway.refresh_seller_token.return_value = oauth_result

        use_case = RefreshInstructorTokenUseCase(
            mock_instructor_repo, mock_payment_gateway
        )
        result = await use_case.execute(connected_instructor_profile.user_id)

        assert result is True
        mock_payment_gateway.refresh_seller_token.assert_called_once_with(
            refresh_token="decrypted_refresh_token"
        )
        mock_instructor_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_refresh_not_needed(
        self,
        mock_instructor_repo,
        mock_payment_gateway,
        connected_instructor_profile,
    ):
        """Não deve renovar se token não está próximo de expirar."""
        # Token expirando em 90 dias (acima do threshold de 30)
        connected_instructor_profile.mp_token_expiry = datetime.now(
            timezone.utc
        ).replace(tzinfo=None) + timedelta(days=90)

        mock_instructor_repo.get_by_user_id.return_value = connected_instructor_profile

        use_case = RefreshInstructorTokenUseCase(
            mock_instructor_repo, mock_payment_gateway
        )
        result = await use_case.execute(connected_instructor_profile.user_id)

        assert result is False
        mock_payment_gateway.refresh_seller_token.assert_not_called()
        mock_instructor_repo.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_refresh_no_mp_account_raises(
        self,
        mock_instructor_repo,
        mock_payment_gateway,
        instructor_profile,
    ):
        """Deve lançar erro se instrutor não tiver conta MP."""
        mock_instructor_repo.get_by_user_id.return_value = instructor_profile

        use_case = RefreshInstructorTokenUseCase(
            mock_instructor_repo, mock_payment_gateway
        )

        with pytest.raises(ValueError, match="não possui conta Mercado Pago"):
            await use_case.execute(instructor_profile.user_id)
