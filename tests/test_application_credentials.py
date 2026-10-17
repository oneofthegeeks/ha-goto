"""Token exchange must carry client creds in a Basic header, not the body."""
import base64

from homeassistant.components.application_credentials import ClientCredential
from homeassistant.core import HomeAssistant

from custom_components.goto_sms.application_credentials import (
    GoToBasicAuthImplementation,
    async_get_auth_implementation,
    async_get_authorization_server,
)
from custom_components.goto_sms.const import DOMAIN, OAUTH2_TOKEN_URL

CLIENT_ID = "my-id"
CLIENT_SECRET = "my-secret"
BASIC = "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
TOKEN = {"access_token": "new-at", "refresh_token": "new-rt", "expires_in": 3600}


async def _impl(hass: HomeAssistant) -> GoToBasicAuthImplementation:
    return await async_get_auth_implementation(
        hass, DOMAIN, ClientCredential(CLIENT_ID, CLIENT_SECRET)
    )


def _body(aioclient_mock):
    # mock_calls entries are (method, url, data, headers).
    call = aioclient_mock.mock_calls[0]
    return call[2], call[3]


async def test_authorization_server(hass: HomeAssistant) -> None:
    server = await async_get_authorization_server(hass)
    assert server.authorize_url == "https://authentication.logmeininc.com/oauth/authorize"
    assert server.token_url == "https://authentication.logmeininc.com/oauth/token"


async def test_code_exchange_uses_basic_header(hass, aioclient_mock) -> None:
    aioclient_mock.post(OAUTH2_TOKEN_URL, json=TOKEN)
    impl = await _impl(hass)
    assert isinstance(impl, GoToBasicAuthImplementation)

    result = await impl.async_resolve_external_data(
        {"code": "abc", "state": {"redirect_uri": "https://ha/auth/external/callback"}}
    )

    assert result == TOKEN
    data, headers = _body(aioclient_mock)
    assert headers["Authorization"] == BASIC
    assert data == {
        "grant_type": "authorization_code",
        "code": "abc",
        "redirect_uri": "https://ha/auth/external/callback",
    }


async def test_refresh_uses_basic_header(hass, aioclient_mock) -> None:
    aioclient_mock.post(OAUTH2_TOKEN_URL, json=TOKEN)
    impl = await _impl(hass)

    result = await impl._async_refresh_token(
        {"access_token": "old", "refresh_token": "old-rt"}
    )

    assert result["access_token"] == "new-at"
    data, headers = _body(aioclient_mock)
    assert headers["Authorization"] == BASIC
    assert data == {"grant_type": "refresh_token", "refresh_token": "old-rt"}
