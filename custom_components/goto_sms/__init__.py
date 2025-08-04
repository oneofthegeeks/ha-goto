"""The GoTo SMS integration."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from . import config_flow
from .const import DOMAIN
from .oauth import GoToOAuth2Manager

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.NOTIFY, Platform.SENSOR]

_LOGGER.info("GoTo SMS integration loaded")


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up GoTo SMS from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Create OAuth manager for this config entry
    oauth_manager = GoToOAuth2Manager(hass, entry)

    # Store the OAuth manager in hass.data for access by other components
    hass.data[DOMAIN][f"{entry.entry_id}_oauth"] = oauth_manager

    # Validate and refresh tokens on startup
    async def startup_token_validation():
        """Validate and refresh tokens on startup."""
        try:
            _LOGGER.info("Running startup token validation")

            # Load tokens
            if not oauth_manager.load_tokens():
                _LOGGER.warning("No tokens found during startup validation")
                return

            # Check if tokens need refresh
            if not oauth_manager._validate_tokens():
                _LOGGER.info("Tokens need refresh on startup, refreshing...")
                if oauth_manager.refresh_tokens():
                    _LOGGER.info("Startup token refresh successful")
                else:
                    _LOGGER.warning("Startup token refresh failed")
            else:
                _LOGGER.info("Tokens are valid on startup")

        except Exception as e:
            _LOGGER.error("Error during startup token validation: %s", e)

    # Run startup validation after a short delay to ensure everything is loaded
    hass.async_create_task(
        asyncio.sleep(5)  # Wait 5 seconds for everything to initialize
    ).add_done_callback(lambda _: hass.async_create_task(startup_token_validation()))

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

    # Set up periodic token refresh
    async def refresh_tokens_periodic(now):
        """Periodically refresh tokens to keep them fresh."""
        try:
            _LOGGER.debug("Running periodic token refresh check")

            # Load tokens if not already loaded
            if not oauth_manager._tokens:
                if not oauth_manager.load_tokens():
                    _LOGGER.warning("No tokens available for periodic refresh")
                    return

            # Check if tokens need refresh (using the same validation logic)
            if not oauth_manager._validate_tokens():
                _LOGGER.info("Proactively refreshing tokens before expiry")
                if oauth_manager.refresh_tokens():
                    _LOGGER.info("Periodic token refresh successful")
                else:
                    _LOGGER.warning("Periodic token refresh failed")
            else:
                _LOGGER.debug("Tokens are still valid, no refresh needed")

        except Exception as e:
            _LOGGER.error("Error during periodic token refresh: %s", e)

    # Run token refresh every 30 minutes
    entry.async_on_unload(
        async_track_time_interval(hass, refresh_tokens_periodic, timedelta(minutes=30))
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
            hass.data[DOMAIN].pop(f"{entry.entry_id}_oauth", None)

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
