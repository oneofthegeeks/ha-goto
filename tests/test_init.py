"""Entry setup, reauth surfacing, unload."""
import time

from homeassistant.components.application_credentials import (
    ClientCredential,
    async_import_client_credential,
)
from homeassistant.components.notify.legacy import NOTIFY_SERVICES
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.goto_sms.const import DOMAIN


async def test_setup_and_unload(hass: HomeAssistant, setup_entry, messaging) -> None:
    assert setup_entry.state is ConfigEntryState.LOADED
    assert hass.services.has_service(DOMAIN, "send_sms")
    assert hass.services.has_service("notify", DOMAIN)
    assert setup_entry.runtime_data.messaging is messaging

    assert await hass.config_entries.async_unload(setup_entry.entry_id)
    assert setup_entry.state is ConfigEntryState.NOT_LOADED
    # Global action stays registered (action-setup rule); notify shim is removed.
    assert hass.services.has_service(DOMAIN, "send_sms")
    assert not hass.services.has_service("notify", DOMAIN)
    assert DOMAIN not in hass.data[NOTIFY_SERVICES]

    # Reload brings the legacy notify service back.
    assert await hass.config_entries.async_setup(setup_entry.entry_id)
    await hass.async_block_till_done()
    assert hass.services.has_service("notify", DOMAIN)


async def test_token_provider_returns_access_token(setup_entry, messaging) -> None:
    provider = messaging.cls.call_args.args[0]
    assert await provider() == "at"


async def test_missing_refresh_token_starts_reauth(hass: HomeAssistant, messaging) -> None:
    """A migrated v1 entry with no tokens must go to reauth, never refresh None."""
    assert await async_setup_component(hass, "application_credentials", {})
    await async_import_client_credential(hass, DOMAIN, ClientCredential("cid", "s"))
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=2,
        data={
            "auth_implementation": DOMAIN,
            "token": {
                "access_token": None,
                "refresh_token": None,
                "expires_at": 0.0,
                "token_type": "Bearer",
                "scope": "messaging.v1.send",
            },
        },
    )
    entry.add_to_hass(hass)
    assert not await hass.config_entries.async_setup(entry.entry_id)
    assert entry.state is ConfigEntryState.SETUP_ERROR
    assert any(
        f["context"]["source"] == "reauth"
        for f in hass.config_entries.flow.async_progress()
    )


async def test_missing_credentials_starts_reauth(hass: HomeAssistant, messaging, v2_entry) -> None:
    assert await async_setup_component(hass, "application_credentials", {})
    v2_entry.add_to_hass(hass)
    assert not await hass.config_entries.async_setup(v2_entry.entry_id)
    assert v2_entry.state is ConfigEntryState.SETUP_ERROR


# --- token refresh failure mapping (real provider, mocked token endpoint) ---
import aiohttp
import pytest
from homeassistant.exceptions import HomeAssistantError

from custom_components.goto_sms.const import OAUTH2_TOKEN_URL


def _expired(entry: MockConfigEntry) -> dict:
    return {**entry.data, "token": {**entry.data["token"], "expires_at": time.time() - 10}}


def _has_reauth(hass) -> bool:
    return any(
        f["context"]["source"] == "reauth"
        for f in hass.config_entries.flow.async_progress()
    )


async def _setup_expired(hass, messaging, v2_entry) -> None:
    assert await async_setup_component(hass, "application_credentials", {})
    await async_import_client_credential(hass, DOMAIN, ClientCredential("cid", "s"))
    v2_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(v2_entry, data=_expired(v2_entry))
    await hass.config_entries.async_setup(v2_entry.entry_id)
    await hass.async_block_till_done()


async def test_refresh_400_at_setup_reauths(hass, messaging, v2_entry, aioclient_mock) -> None:
    aioclient_mock.post(OAUTH2_TOKEN_URL, status=400, json={"error": "invalid_grant"})
    await _setup_expired(hass, messaging, v2_entry)
    assert v2_entry.state is ConfigEntryState.SETUP_ERROR
    assert _has_reauth(hass)


@pytest.mark.parametrize(
    "mock_kwargs",
    [{"status": 429}, {"status": 503}, {"exc": aiohttp.ClientError()}, {"exc": TimeoutError()}],
)
async def test_refresh_transient_at_setup_retries(
    hass, messaging, v2_entry, aioclient_mock, mock_kwargs
) -> None:
    aioclient_mock.post(OAUTH2_TOKEN_URL, **mock_kwargs)
    await _setup_expired(hass, messaging, v2_entry)
    assert v2_entry.state is ConfigEntryState.SETUP_RETRY
    assert not _has_reauth(hass)


async def test_refresh_400_mid_send_reauths(
    hass, aioclient_mock, setup_entry, messaging
) -> None:
    provider = messaging.cls.call_args.args[0]
    async def via_provider(*args):
        return await provider()

    messaging.async_send_sms.side_effect = via_provider
    hass.config_entries.async_update_entry(setup_entry, data=_expired(setup_entry))
    aioclient_mock.post(OAUTH2_TOKEN_URL, status=400, json={"error": "invalid_grant"})
    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            DOMAIN,
            "send_sms",
            {"message": "m", "target": "+15550001111", "sender_id": "+15552223333"},
            blocking=True,
        )
    await hass.async_block_till_done()
    assert _has_reauth(hass)


async def test_refresh_timeout_mid_send_is_clean_error(
    hass, aioclient_mock, setup_entry, messaging
) -> None:
    provider = messaging.cls.call_args.args[0]
    async def via_provider(*args):
        return await provider()

    messaging.async_send_sms.side_effect = via_provider
    hass.config_entries.async_update_entry(setup_entry, data=_expired(setup_entry))
    aioclient_mock.post(OAUTH2_TOKEN_URL, exc=TimeoutError())
    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            DOMAIN,
            "send_sms",
            {"message": "m", "target": "+15550001111", "sender_id": "+15552223333"},
            blocking=True,
        )
    assert not _has_reauth(hass)
