"""The GoTo SMS integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from aiohttp import ClientError, ClientResponseError
from aiogotoconnect import GoToAuthError, GoToError, GoToMessaging
from homeassistant.components.notify.legacy import NOTIFY_SERVICES
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import discovery
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.config_entry_oauth2_flow import (
    OAuth2Session,
    async_get_config_entry_implementation,
)
from homeassistant.helpers.typing import ConfigType
from homeassistant.util.hass_dict import HassKey

from .const import DOMAIN
from .migration import async_migrate_entry  # noqa: F401  (HA looks it up here)
from .services import async_setup_services

_LOGGER = logging.getLogger(__name__)

DATA_HASS_CONFIG: HassKey[ConfigType] = HassKey(f"{DOMAIN}_hass_config")
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


@dataclass
class GoToData:
    """Runtime objects for a loaded entry."""

    messaging: GoToMessaging
    session: OAuth2Session


type GoToConfigEntry = ConfigEntry[GoToData]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the action once, independent of entries."""
    async_setup_services(hass)
    hass.data[DATA_HASS_CONFIG] = config  # legacy notify loading needs the real config
    return True


async def async_setup_entry(hass: HomeAssistant, entry: GoToConfigEntry) -> bool:
    """Set up GoTo SMS from a config entry."""
    # A migrated v1 entry that never had tokens must reauth, not refresh None.
    if not entry.data.get("token", {}).get("refresh_token"):
        raise ConfigEntryAuthFailed("No refresh token; sign in to GoTo again")

    try:
        implementation = await async_get_config_entry_implementation(hass, entry)
    except ValueError as err:  # client credentials missing (e.g. v1 had none)
        raise ConfigEntryAuthFailed("GoTo client credentials are missing") from err

    session = OAuth2Session(hass, entry, implementation)

    async def _token() -> str:
        """Token provider for aiogotoconnect; maps refresh failures to its errors."""
        try:
            await session.async_ensure_token_valid()
        except ClientResponseError as err:
            if err.status in (400, 401, 403):  # 408/429/5xx are transient
                raise GoToAuthError("Token refresh rejected") from err
            raise GoToError("Token refresh failed") from err
        except (ClientError, TimeoutError) as err:
            raise GoToError("Token refresh failed") from err
        return session.token["access_token"]

    try:
        await _token()  # surface a dead refresh token at setup, not first send
    except GoToAuthError as err:
        raise ConfigEntryAuthFailed(str(err)) from err
    except GoToError as err:
        raise ConfigEntryNotReady(str(err)) from err

    entry.runtime_data = GoToData(
        messaging=GoToMessaging(_token, session=async_get_clientsession(hass)),
        session=session,
    )

    # Legacy notify.goto_sms: discovery name makes the service "goto_sms".
    await discovery.async_load_platform(
        hass, "notify", DOMAIN, {CONF_NAME: DOMAIN}, hass.data[DATA_HASS_CONFIG]
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: GoToConfigEntry) -> bool:
    """Unload: drop the legacy notify service so a reload can re-register it."""
    hass.services.async_remove("notify", DOMAIN)
    # Without this the dispatcher would see a stale service object on reload.
    hass.data.get(NOTIFY_SERVICES, {}).pop(DOMAIN, None)
    return True
