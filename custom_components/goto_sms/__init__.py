"""The GoTo SMS integration."""

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from . import config_flow
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.NOTIFY]

_LOGGER.info("GoTo SMS integration loaded")


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up GoTo SMS from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Register the SMS service with proper schema
    async def handle_send_sms(call):
        """Handle the send SMS service call."""
        from .notify import get_service

        notify_service = get_service(hass, {})
        if notify_service:
            message = call.data.get("message")
            target = call.data.get("target")
            sender_id = call.data.get("sender_id")

            if notify_service:
                await notify_service.async_send_message_service(call)

    # Register the service with schema for form interface
    hass.services.async_register(
        DOMAIN,
        "send_sms",
        handle_send_sms,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    try:
        # Remove the service
        hass.services.async_remove(DOMAIN, "send_sms")

        # Clean up the data
        if DOMAIN in hass.data:
            hass.data[DOMAIN].pop(entry.entry_id, None)

        _LOGGER.info("GoTo SMS integration unloaded successfully")
        return True
    except Exception as e:
        _LOGGER.error("Error unloading GoTo SMS integration: %s", e)
        return False


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the GoTo SMS component."""
    _LOGGER.info("Setting up GoTo SMS integration")
    hass.data.setdefault(DOMAIN, {})

    # The notification service will be registered by the notify platform
    # when the integration is loaded via config entry

    _LOGGER.info("GoTo SMS integration setup complete")
    return True
