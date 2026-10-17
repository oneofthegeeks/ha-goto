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
