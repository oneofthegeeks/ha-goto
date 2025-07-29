"""GoTo SMS notification service."""

import logging
from typing import Any, Dict, Optional

import requests
from homeassistant.components.notify import (
    ATTR_MESSAGE,
    ATTR_TARGET,
    BaseNotificationService,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import (
    DOMAIN,
    GOTO_API_BASE_URL,
    SMS_ENDPOINT,
    ATTR_SENDER_ID,
    DEFAULT_SENDER_ID,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
)
from .oauth import GoToOAuth2Manager

_LOGGER = logging.getLogger(__name__)


def get_service(
    hass: HomeAssistant,
    config: ConfigType,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> "GoToSMSNotificationService":
    """Get the GoTo SMS notification service."""
    # Get the config entry for this integration
    config_entries = hass.config_entries.async_entries(DOMAIN)
    if not config_entries:
        _LOGGER.error("No GoTo SMS configuration found")
        return None
    
    config_entry = config_entries[0]  # Use the first config entry
    oauth_manager = GoToOAuth2Manager(hass, config_entry)
    
    return GoToSMSNotificationService(hass, oauth_manager)


class GoToSMSNotificationService(BaseNotificationService):
    """GoTo SMS notification service."""

    def __init__(self, hass: HomeAssistant, oauth_manager: GoToOAuth2Manager):
        """Initialize the service."""
        self.hass = hass
        self.oauth_manager = oauth_manager

    async def async_send_message(self, message: str, **kwargs: Any) -> None:
        """Send SMS message."""
        _LOGGER.info("Received SMS request - message: %s, kwargs: %s", message, kwargs)
        
        target = kwargs.get(ATTR_TARGET)
        sender_id = kwargs.get(ATTR_SENDER_ID)

        _LOGGER.info("Extracted target: %s, sender_id: %s", target, sender_id)

        if not target:
            _LOGGER.error("No target phone number provided")
            return

        if not message:
            _LOGGER.error("No message provided")
            return

        if not sender_id:
            _LOGGER.error("No sender_id provided. You must specify the GoTo phone number in E.164 format to send from.")
            return

        # Run the SMS sending in a thread to avoid blocking
        await self.hass.async_add_executor_job(
            self._send_sms, message, target, sender_id
        )

    def _send_sms(self, message: str, target: str, sender_id: str) -> None:
        """Send SMS message via GoTo Connect API."""
        try:
            headers = self.oauth_manager.get_headers()
            if not headers:
                _LOGGER.error("Failed to get valid authentication headers")
                return

            # Prepare the SMS payload according to GoTo Connect API specification
            payload = {
                "ownerPhoneNumber": sender_id,  # The GoTo phone number to send from
                "contactPhoneNumbers": [target],  # List of phone numbers to send to
                "body": message,  # The message content
            }

            url = f"{GOTO_API_BASE_URL}{SMS_ENDPOINT}"
            
            _LOGGER.info("Sending SMS to %s: %s", target, message[:50] + "..." if len(message) > 50 else message)
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=30,
            )

            if response.status_code == 200:
                _LOGGER.info("SMS sent successfully to %s", target)
            elif response.status_code == 401:
                _LOGGER.error("Authentication failed. Token may be expired.")
                # Try to refresh token and retry once
                if self.oauth_manager.refresh_tokens():
                    headers = self.oauth_manager.get_headers()
                    if headers:
                        response = requests.post(
                            url,
                            headers=headers,
                            json=payload,
                            timeout=30,
                        )
                        if response.status_code == 200:
                            _LOGGER.info("SMS sent successfully after token refresh")
                            return
                
                _LOGGER.error("Failed to send SMS after token refresh")
            else:
                _LOGGER.error(
                    "Failed to send SMS. Status: %d, Response: %s",
                    response.status_code,
                    response.text,
                )

        except requests.exceptions.RequestException as e:
            _LOGGER.error("Network error while sending SMS: %s", e)
        except Exception as e:
            _LOGGER.error("Unexpected error while sending SMS: %s", e) 