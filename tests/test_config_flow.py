"""OAuth config flow: happy path, single-instance abort, reauth."""
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import pytest
from homeassistant import config_entries
from homeassistant.components.application_credentials import (
    ClientCredential,
    async_import_client_credential,
)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.goto_sms.const import DOMAIN, OAUTH2_TOKEN_URL

CLIENT_ID = "my-id"
CLIENT_SECRET = "my-secret"
REDIRECT = "https://example.com/auth/external/callback"
TOKEN = {
    "access_token": "new-at",
    "refresh_token": "new-rt",
    "token_type": "Bearer",
    "expires_in": 3600,
}


@pytest.fixture(autouse=True)
async def setup_credentials(hass: HomeAssistant) -> None:
    """Register application credentials so the flow has an implementation."""
    assert await async_setup_component(hass, "application_credentials", {})
    await async_import_client_credential(
        hass, DOMAIN, ClientCredential(CLIENT_ID, CLIENT_SECRET)
    )


@pytest.fixture(autouse=True)
def no_entry_setup():
    """Flow tests must not run the (v1) entry setup."""
    with patch("custom_components.goto_sms.async_setup_entry", return_value=True) as m:
        yield m


async def _walk_oauth(hass, hass_client_no_auth, aioclient_mock, result):
    """Drive the external step through the callback and token exchange."""
    assert result["type"] is FlowResultType.EXTERNAL_STEP
    state = config_entry_oauth2_flow._encode_jwt(
        hass, {"flow_id": result["flow_id"], "redirect_uri": REDIRECT}
    )
    client = await hass_client_no_auth()
    resp = await client.get(f"/auth/external/callback?code=abcd&state={state}")
    assert resp.status == 200
    aioclient_mock.post(OAUTH2_TOKEN_URL, json=TOKEN)
    return await hass.config_entries.flow.async_configure(result["flow_id"])


@pytest.mark.usefixtures("current_request_with_host")
async def test_full_flow(hass, hass_client_no_auth, aioclient_mock) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    # Exactly one scope param (the implementation adds it; the flow must not).
    query = parse_qs(urlparse(result["url"]).query)
    assert query["scope"] == ["messaging.v1.send"]
    assert result["url"].count("scope=") == 1

    result = await _walk_oauth(hass, hass_client_no_auth, aioclient_mock, result)

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "GoTo Connect"
    assert result["data"]["token"]["access_token"] == "new-at"
    assert result["data"]["token"]["refresh_token"] == "new-rt"
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    assert entry.unique_id == DOMAIN
    assert (entry.version, entry.minor_version) == (2, 1)


@pytest.mark.usefixtures("current_request_with_host")
async def test_second_instance_aborts(hass, hass_client_no_auth, aioclient_mock) -> None:
    MockConfigEntry(domain=DOMAIN, unique_id=DOMAIN, data={}).add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    # unique_id is only known after the token exchange, so the abort fires then.
    result = await _walk_oauth(hass, hass_client_no_auth, aioclient_mock, result)
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


@pytest.mark.usefixtures("current_request_with_host")
async def test_reauth(hass, hass_client_no_auth, aioclient_mock) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=DOMAIN,
        version=2,
        minor_version=1,
        data={
            "auth_implementation": DOMAIN,
            "token": {"access_token": "old-at", "refresh_token": "old-rt"},
        },
    )
    entry.add_to_hass(hass)

    result = await entry.start_reauth_flow(hass)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"

    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    result = await _walk_oauth(hass, hass_client_no_auth, aioclient_mock, result)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"
    assert len(hass.config_entries.async_entries(DOMAIN)) == 1
    assert entry.data["token"]["access_token"] == "new-at"
    assert entry.data["token"]["refresh_token"] == "new-rt"
