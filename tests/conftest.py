"""Shared pytest fixtures."""
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.components.application_credentials import (
    ClientCredential,
    async_import_client_credential,
)
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.goto_sms.const import DOMAIN


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Let HA load custom_components/ in every test."""
    yield


@pytest.fixture
def messaging():
    """Patch the gotoconnect client at the integration boundary."""
    client = MagicMock()
    client.async_send_sms = AsyncMock(return_value={"id": "msg-1"})
    with patch("custom_components.goto_sms.GoToMessaging", return_value=client) as cls:
        client.cls = cls
        yield client


@pytest.fixture
def v2_entry() -> MockConfigEntry:
    """A migrated/fresh v2 entry with a still-valid token."""
    return MockConfigEntry(
        domain=DOMAIN,
        version=2,
        unique_id=DOMAIN,
        data={
            "auth_implementation": DOMAIN,
            "token": {
                "access_token": "at",
                "refresh_token": "rt",
                "expires_at": time.time() + 3600,
                "token_type": "Bearer",
                "scope": "messaging.v1.send",
            },
        },
    )


@pytest.fixture
async def setup_entry(hass: HomeAssistant, messaging, v2_entry):
    """Set up the integration with credentials registered; returns the entry."""
    assert await async_setup_component(hass, "application_credentials", {})
    await async_import_client_credential(
        hass, DOMAIN, ClientCredential("cid", "csecret")
    )
    v2_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(v2_entry.entry_id)
    await hass.async_block_till_done()
    return v2_entry
