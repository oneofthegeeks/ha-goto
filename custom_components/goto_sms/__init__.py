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

_LOGGER.info("GoTo SMS integration loaded")


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up GoTo SMS from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Register the notification service
    from .notify import get_service
    
    notify_service = get_service(hass, {})
    if notify_service:
        async def handle_sms_service(call):
            """Handle the SMS service call."""
            message = call.data.get("message")
            target = call.data.get("target")
            sender_id = call.data.get("sender_id")
            
            # Validate required parameters
            if not message:
                _LOGGER.error("No message provided")
                return
                
            if not target:
                _LOGGER.error("No target phone number provided")
                return
                
            if not sender_id:
                _LOGGER.error("No sender_id provided. You must specify the GoTo phone number in E.164 format to send from.")
                return
            
            if notify_service:
                await notify_service.async_send_message(message, target=target, sender_id=sender_id)
        
        hass.services.async_register(
            "notify",
            "goto_sms",
            handle_sms_service,
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the GoTo SMS component."""
    _LOGGER.info("Setting up GoTo SMS integration")
    hass.data.setdefault(DOMAIN, {})
    
    # The notification service will be registered by the notify platform
    # when the integration is loaded via config entry
    
    _LOGGER.info("GoTo SMS integration setup complete")
    return True 