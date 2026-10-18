"""v1 -> v2 entry migration: credentials imported, token reshaped, no re-auth."""
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.components.application_credentials import DATA_COMPONENT
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.goto_sms.const import DOMAIN
from custom_components.goto_sms.migration import async_migrate_entry

# Real v1 shape (config_flow.py on main, oauth.py save_tokens): tokens are
# NESTED under "tokens"; expiry is a naive local-time ISO string.
ISO = "2026-10-17T12:30:45.123456"


def v1_entry(**tokens) -> MockConfigEntry:
    nested = {"access_token": "old-at", "refresh_token": "old-rt", **tokens}
    return MockConfigEntry(
        domain=DOMAIN,
        version=1,
        data={"client_id": "cid", "client_secret": "csecret", "tokens": nested},
    )


@pytest.fixture(autouse=True)
async def creds(hass: HomeAssistant) -> None:
    assert await async_setup_component(hass, "application_credentials", {})


async def migrate(hass, entry):
    entry.add_to_hass(hass)
    return await async_migrate_entry(hass, entry)


async def test_iso_expiry_migrates(hass: HomeAssistant) -> None:
    entry = v1_entry(token_expires_at=ISO)
    assert await migrate(hass, entry) is True
    assert (entry.version, entry.minor_version) == (2, 1)
    assert entry.data == {
        "auth_implementation": DOMAIN,
        "token": {
            "access_token": "old-at",
            "refresh_token": "old-rt",
            "expires_at": datetime.fromisoformat(ISO).timestamp(),
            "token_type": "Bearer",
            "scope": "messaging.v1.send",
        },
    }
    stored = hass.data[DATA_COMPONENT].async_client_credentials(DOMAIN)[DOMAIN]
    assert (stored.client_id, stored.client_secret) == ("cid", "csecret")


async def test_top_level_keys_and_epoch_expiry(hass: HomeAssistant) -> None:
    """Brief/constraints list flat keys; accept them too."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=1,
        data={
            "client_id": "cid",
            "client_secret": "csecret",
            "access_token": "at",
            "refresh_token": "rt",
            "token_expires_at": 1800000000,
        },
    )
    assert await migrate(hass, entry) is True
    assert entry.data["token"]["expires_at"] == 1800000000.0
    assert entry.data["token"]["refresh_token"] == "rt"


@pytest.mark.parametrize("bad", ["garbage", None, "", {"x": 1}])
async def test_bad_expiry_forces_refresh(hass: HomeAssistant, bad) -> None:
    entry = v1_entry(token_expires_at=bad)
    assert await migrate(hass, entry) is True
    assert entry.data["token"]["expires_at"] == 0.0


async def test_missing_expiry_forces_refresh(hass: HomeAssistant) -> None:
    entry = v1_entry()
    assert await migrate(hass, entry) is True
    assert entry.data["token"]["expires_at"] == 0.0


async def test_missing_creds_and_tokens_still_migrates(hass: HomeAssistant) -> None:
    """Never brick the entry: shape migrates, reauth happens later."""
    entry = MockConfigEntry(domain=DOMAIN, version=1, data={})
    assert await migrate(hass, entry) is True
    assert entry.version == 2
    assert entry.data["auth_implementation"] == DOMAIN
    assert entry.data["token"]["expires_at"] == 0.0
    assert hass.data[DATA_COMPONENT].async_client_credentials(DOMAIN) == {}


async def test_future_version_refused(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(domain=DOMAIN, version=3, data={"keep": 1})
    assert await migrate(hass, entry) is False
    assert entry.data == {"keep": 1}


async def test_current_version_untouched(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(domain=DOMAIN, version=2, data={"keep": 1})
    assert await migrate(hass, entry) is True
    assert entry.data == {"keep": 1}


async def test_hook_wired_through_core(hass: HomeAssistant) -> None:
    """HA calls the integration's async_migrate_entry on a v1 entry."""
    entry = v1_entry(token_expires_at=ISO)
    entry.add_to_hass(hass)
    with patch("custom_components.goto_sms.async_setup_entry", return_value=True):
        await hass.config_entries.async_setup(entry.entry_id)
    assert entry.version == 2
    assert entry.state is ConfigEntryState.LOADED


async def test_migrated_v1_entry_sets_up_and_sends(hass: HomeAssistant) -> None:
    """End to end: v1 entry -> HA runs migration -> setup -> send_sms, no re-auth."""
    entry = v1_entry(token_expires_at="2099-01-01T00:00:00")
    entry.add_to_hass(hass)
    with patch("custom_components.goto_sms.GoToMessaging") as cls:
        cls.return_value.async_send_sms = AsyncMock(return_value={"id": "m"})
        assert await hass.config_entries.async_setup(entry.entry_id)
        assert entry.state is ConfigEntryState.LOADED
        assert entry.version == 2
        out = await hass.services.async_call(
            DOMAIN,
            "send_sms",
            {"message": "hi {{ n }}", "target": "+15550001111", "sender_id": "+15552223333", "data": {"n": 1}},
            blocking=True,
            return_response=True,
        )
        assert out == {"id": "m"}
        cls.return_value.async_send_sms.assert_awaited_once_with(
            "+15552223333", ["+15550001111"], "hi 1"
        )
        # The provider hands the lib the migrated (still valid) access token.
        assert await cls.call_args.args[0]() == "old-at"
    assert not hass.config_entries.flow.async_progress()


async def test_migrated_v1_entry_without_tokens_reauths(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN, version=1, data={"client_id": "cid", "client_secret": "s"}
    )
    entry.add_to_hass(hass)
    assert not await hass.config_entries.async_setup(entry.entry_id)
    assert any(
        f["context"]["source"] == "reauth"
        for f in hass.config_entries.flow.async_progress()
    )


# --- C1: migrated entries get unique_id so reauth / duplicate guard work ---
import logging

from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import config_entry_oauth2_flow

from custom_components.goto_sms.const import OAUTH2_TOKEN_URL

REDIRECT = "https://example.com/auth/external/callback"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


async def _complete_reauth(hass, hass_client_no_auth, aioclient_mock) -> None:
    flows = [
        f for f in hass.config_entries.flow.async_progress()
        if f["context"]["source"] == "reauth"
    ]
    assert flows
    fid = flows[0]["flow_id"]
    result = await hass.config_entries.flow.async_configure(fid, {})
    assert result["type"] is FlowResultType.EXTERNAL_STEP
    state = config_entry_oauth2_flow._encode_jwt(
        hass, {"flow_id": fid, "redirect_uri": REDIRECT}
    )
    client = await hass_client_no_auth()
    await client.get(f"/auth/external/callback?code=abcd&state={state}")
    aioclient_mock.clear_requests()
    aioclient_mock.post(
        OAUTH2_TOKEN_URL,
        json={
            "access_token": "n",
            "refresh_token": "n2",
            "token_type": "Bearer",
            "expires_in": 3600,
        },
    )
    result = await hass.config_entries.flow.async_configure(fid)
    assert result["reason"] == "reauth_successful"


@pytest.mark.usefixtures("current_request_with_host")
async def test_migrated_v1_reauth_completes(
    hass: HomeAssistant, hass_client_no_auth, aioclient_mock
) -> None:
    entry = v1_entry(token_expires_at="2000-01-01T00:00:00")
    entry.add_to_hass(hass)
    aioclient_mock.post(OAUTH2_TOKEN_URL, status=400, json={"error": "invalid_grant"})
    assert not await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.version == 2
    assert entry.unique_id == DOMAIN
    assert entry.state is ConfigEntryState.SETUP_ERROR

    await _complete_reauth(hass, hass_client_no_auth, aioclient_mock)
    await hass.async_block_till_done()
    assert entry.data["token"]["refresh_token"] == "n2"
    assert len(hass.config_entries.async_entries(DOMAIN)) == 1


@pytest.mark.usefixtures("current_request_with_host")
async def test_migrated_v1_without_tokens_reauth_completes(
    hass: HomeAssistant, hass_client_no_auth, aioclient_mock
) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=1,
        data={"client_id": "cid", "client_secret": "cs"},
    )
    entry.add_to_hass(hass)
    assert not await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.unique_id == DOMAIN
    assert entry.state is ConfigEntryState.SETUP_ERROR

    await _complete_reauth(hass, hass_client_no_auth, aioclient_mock)
    await hass.async_block_till_done()
    assert entry.data["token"]["refresh_token"] == "n2"
    assert len(hass.config_entries.async_entries(DOMAIN)) == 1


async def test_second_v1_entry_keeps_no_unique_id(
    hass: HomeAssistant, caplog: pytest.LogCaptureFixture
) -> None:
    first, second = v1_entry(), v1_entry()
    assert await migrate(hass, first)
    with caplog.at_level(logging.WARNING):
        assert await migrate(hass, second)
    assert first.unique_id == DOMAIN
    assert second.unique_id is None
    assert second.version == 2
    assert "already uses unique_id" in caplog.text


@pytest.mark.usefixtures("current_request_with_host")
async def test_duplicate_add_aborts_for_migrated_entry(
    hass: HomeAssistant, hass_client_no_auth, aioclient_mock
) -> None:
    entry = v1_entry(token_expires_at="2000-01-01T00:00:00")
    assert await migrate(hass, entry)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    assert result["type"] is FlowResultType.EXTERNAL_STEP
    fid = result["flow_id"]
    state = config_entry_oauth2_flow._encode_jwt(
        hass, {"flow_id": fid, "redirect_uri": REDIRECT}
    )
    client = await hass_client_no_auth()
    await client.get(f"/auth/external/callback?code=abcd&state={state}")
    aioclient_mock.post(
        OAUTH2_TOKEN_URL,
        json={"access_token": "n", "refresh_token": "n2",
              "token_type": "Bearer", "expires_in": 3600},
    )
    result = await hass.config_entries.flow.async_configure(fid)
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
