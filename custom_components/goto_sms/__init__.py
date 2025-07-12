"""The GoTo SMS integration."""

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = []

# Import config flow
from . import config_flow


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up GoTo SMS from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the GoTo SMS component."""
    hass.data.setdefault(DOMAIN, {})
    
    # Register the notification service
    hass.services.async_register(
        DOMAIN,
        "send_sms",
        lambda service: _handle_send_sms(hass, service),
    )
    
    return True


def _handle_send_sms(hass: HomeAssistant, service) -> None:
    """Handle the send_sms service call."""
    from .notify import get_service
    
    notify_service = get_service(hass, {})
    notify_service.async_send_message(
        message=service.data.get("message"),
        target=service.data.get("target"),
        sender_id=service.data.get("sender_id"),
    ) 