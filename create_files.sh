#!/bin/bash

# Script to manually create GoTo SMS integration files
# Run this from your Home Assistant Web Terminal

echo "Creating GoTo SMS integration files..."

# Create the directory structure
mkdir -p /config/custom_components/goto_sms/translations/en

# Create __init__.py
cat > /config/custom_components/goto_sms/__init__.py << 'EOF'
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
    _LOGGER.info("Setting up GoTo SMS integration")
    hass.data.setdefault(DOMAIN, {})
    
    # Register the notification service
    hass.services.async_register(
        DOMAIN,
        "send_sms",
        lambda service: _handle_send_sms(hass, service),
    )
    
    _LOGGER.info("GoTo SMS integration setup complete")
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
EOF

# Create const.py
cat > /config/custom_components/goto_sms/const.py << 'EOF'
"""Constants for the GoTo SMS integration."""

DOMAIN = "goto_sms"
DEFAULT_NAME = "GoTo SMS"

# OAuth2 Configuration
OAUTH2_AUTHORIZE_URL = "https://authentication.logmeininc.com/oauth/authorize"
OAUTH2_TOKEN_URL = "https://authentication.logmeininc.com/oauth/token"
OAUTH2_SCOPE = "sms:send"

# GoTo Connect API Endpoints
GOTO_API_BASE_URL = "https://api.goto.com"
SMS_ENDPOINT = "/v1/sms/messages"

# Configuration keys
CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"
CONF_ACCESS_TOKEN = "access_token"
CONF_REFRESH_TOKEN = "refresh_token"
CONF_TOKEN_EXPIRES_AT = "token_expires_at"

# Service configuration
SERVICE_SEND_SMS = "send_sms"
ATTR_MESSAGE = "message"
ATTR_TARGET = "target"
ATTR_SENDER_ID = "sender_id"

# Default values
DEFAULT_SENDER_ID = "HomeAssistant"
EOF

# Create manifest.json
cat > /config/custom_components/goto_sms/manifest.json << 'EOF'
{
  "domain": "goto_sms",
  "name": "GoTo SMS",
  "documentation": "https://github.com/oneofthegeeks/ha-goto",
  "dependencies": [],
  "codeowners": ["@oneofthegeeks"],
  "requirements": [
    "requests>=2.25.1",
    "requests-oauthlib>=1.3.0"
  ],
  "iot_class": "cloud_polling",
  "version": "1.0.0",
  "config_flow": true,
  "integration_type": "service"
}
EOF

echo "Files created successfully!"
echo "Now restart Home Assistant to load the integration."
EOF 