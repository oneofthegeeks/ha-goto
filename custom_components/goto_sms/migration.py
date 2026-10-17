"""Migrate v1 config entries (own OAuth) to v2 (application credentials)."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from homeassistant.components.application_credentials import (
    ClientCredential,
    async_import_client_credential,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from .const import DOMAIN, OAUTH_SCOPES

_LOGGER = logging.getLogger(__name__)


def _expires_at(raw: Any) -> float:
    """Epoch seconds from v1's expiry; 0.0 (refresh on first use) if unusable."""
    if isinstance(raw, bool):
        return 0.0
    if isinstance(raw, (int, float)):
        return float(raw)
    if isinstance(raw, str):
        try:
            # v1 wrote datetime.now().isoformat(): naive local time, which
            # .timestamp() interprets as local too.
            return datetime.fromisoformat(raw).timestamp()
        except ValueError:
            pass
    return 0.0


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Upgrade a v1 entry in place; never demands re-auth."""
    if entry.version > 2:
        return False
    if entry.version == 2:
        return True

    # v1 nested tokens under "tokens"; also accept flat keys.
    tokens = entry.data.get("tokens") or entry.data
    client_id = entry.data.get("client_id")
    client_secret = entry.data.get("client_secret")

    if client_id and client_secret:
        await async_setup_component(hass, "application_credentials", {})
        await async_import_client_credential(
            hass, DOMAIN, ClientCredential(client_id, client_secret)
        )
    else:
        # Migrate anyway; setup will hit reauth rather than bricking the entry.
        _LOGGER.warning("v1 entry has no client credentials; reauth will be needed")

    token = {
        "access_token": tokens.get("access_token"),
        "refresh_token": tokens.get("refresh_token"),
        "expires_at": _expires_at(tokens.get("token_expires_at")),
        "token_type": "Bearer",
        "scope": " ".join(OAUTH_SCOPES),
    }
    hass.config_entries.async_update_entry(
        entry,
        data={"auth_implementation": DOMAIN, "token": token},
        version=2,
        minor_version=1,
    )
    return True
