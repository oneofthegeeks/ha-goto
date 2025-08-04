"""GoTo SMS notification service."""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

import requests
from homeassistant.components.notify import (
    ATTR_MESSAGE,
    ATTR_TARGET,
    BaseNotificationService,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.template import Template, TemplateError
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import (
    ATTR_SENDER_ID,
    ATTR_TEMPLATE_DATA,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    DOMAIN,
    GOTO_API_BASE_URL,
    SMS_ENDPOINT,
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
    _LOGGER.debug("Creating OAuth manager with config entry: %s", config_entry.entry_id)
    oauth_manager = GoToOAuth2Manager(hass, config_entry)

    return GoToSMSNotificationService(hass, oauth_manager)


class GoToSMSNotificationService(BaseNotificationService):
    """GoTo SMS notification service."""

    def __init__(self, hass: HomeAssistant, oauth_manager: GoToOAuth2Manager):
        """Initialize the service."""
        self.hass = hass
        self.oauth_manager = oauth_manager
        _LOGGER.debug("GoToSMSNotificationService initialized")

    async def async_send_message(self, message: str, **kwargs: Any) -> None:
        """Send SMS message."""
        target = kwargs.get(ATTR_TARGET)
        sender_id = kwargs.get(ATTR_SENDER_ID)

        if not target:
            _LOGGER.error("No target phone number provided")
            return

        if not message:
            _LOGGER.error("No message provided")
            return

        if not sender_id:
            _LOGGER.error(
                "No sender_id provided. You must specify the GoTo phone number "
                "in E.164 format to send from."
            )
            return

        # Render template if message contains template syntax
        rendered_message = await self._render_template(message, kwargs.get("data", {}))

        # Call the async SMS sending method directly
        await self._send_sms(rendered_message, target, sender_id)

    async def async_send_message_service(self, call) -> None:
        """Handle the service call for sending SMS."""
        message = call.data.get("message")
        target = call.data.get("target")
        sender_id = call.data.get("sender_id")
        template_data = call.data.get("data", {})

        if not message:
            _LOGGER.error("No message provided")
            return

        if not target:
            _LOGGER.error("No target phone number provided")
            return

        # Render template if message contains template syntax
        rendered_message = await self._render_template(message, template_data)

        # Call the async SMS sending method directly
        await self._send_sms(rendered_message, target, sender_id)

    async def _render_template(
        self, message: str, template_data: Dict[str, Any]
    ) -> str:
        """Render template in message if needed."""
        try:
            # Check if message contains template syntax
            if "{{" in message and "}}" in message:
                _LOGGER.debug("Rendering template: %s", message)

                # Create template object
                template = Template(message, self.hass)

                # Render template with provided data
                rendered = template.async_render(template_data)

                _LOGGER.debug("Template rendered to: %s", rendered)
                return rendered
            else:
                # No template syntax, return as-is
                return message

        except TemplateError as e:
            _LOGGER.error("Template rendering failed: %s", e)
            # Return original message if template fails
            return message
        except Exception as e:
            _LOGGER.error("Unexpected error during template rendering: %s", e)
            return message

    async def _send_sms(self, message: str, target: str, sender_id: str) -> None:
        """Send SMS message via GoTo Connect API."""
        max_retries = 2
        retry_count = 0

        while retry_count <= max_retries:
            try:
                _LOGGER.debug(
                    "Attempting to get authentication headers (attempt %d/%d)",
                    retry_count + 1,
                    max_retries + 1,
                )
                headers = await self.oauth_manager.get_headers()
                if not headers:
                    _LOGGER.error("Failed to get valid authentication headers")
                    _LOGGER.error("Re-authentication has been triggered automatically")
                    _LOGGER.error("Please check your Home Assistant UI for re-authentication prompts")
                    return

                # Prepare the SMS payload according to GoTo Connect API specification
                payload = {
                    "ownerPhoneNumber": sender_id,  # The GoTo phone number to send from
                    "contactPhoneNumbers": [target],  # List of phone numbers to send to
                    "body": message,  # The message content
                }

                url = f"{GOTO_API_BASE_URL}{SMS_ENDPOINT}"

                _LOGGER.info(
                    "Sending SMS to %s: %s",
                    target,
                    message[:50] + "..." if len(message) > 50 else message,
                )

                # Use Home Assistant's async HTTP client
                from homeassistant.helpers.aiohttp_client import async_get_clientsession
                session = async_get_clientsession(self.hass)

                async with session.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=30,
                ) as response:
                    if response.status in [200, 201]:
                        _LOGGER.info("SMS sent successfully to %s", target)
                        return  # Success, exit the retry loop

                    elif response.status == 401:
                        _LOGGER.warning(
                            "Authentication failed (attempt %d/%d). Token may be expired.",
                            retry_count + 1,
                            max_retries + 1,
                        )

                        if retry_count < max_retries:
                            _LOGGER.info("Attempting to refresh tokens and retry...")
                            if await self.oauth_manager.refresh_tokens():
                                _LOGGER.info("Token refresh successful, retrying SMS send...")
                                retry_count += 1
                                continue  # Retry with fresh tokens
                            else:
                                _LOGGER.error("Token refresh failed")
                                break  # Don't retry if refresh failed
                        else:
                            _LOGGER.error("All authentication attempts failed")
                            _LOGGER.error("Re-authentication has been triggered automatically")
                            return

                    elif response.status == 429:  # Rate limited
                        _LOGGER.warning(
                            "Rate limited by GoTo API (attempt %d/%d)",
                            retry_count + 1,
                            max_retries + 1,
                        )
                        if retry_count < max_retries:
                            import asyncio
                            wait_time = 2 ** (
                                retry_count + 1
                            )  # Exponential backoff: 2s, 4s
                            _LOGGER.info("Waiting %d seconds before retry...", wait_time)
                            await asyncio.sleep(wait_time)
                            retry_count += 1
                            continue
                        else:
                            _LOGGER.error("Rate limit exceeded after all retries")
                            return

                    else:
                        response_text = await response.text()
                        _LOGGER.error(
                            "Failed to send SMS. Status: %d, Response: %s",
                            response.status,
                            response_text,
                        )
                        # For other errors, don't retry unless it's a network issue
                        break

            except Exception as e:
                _LOGGER.error(
                    "Network error while sending SMS (attempt %d/%d): %s",
                    retry_count + 1,
                    max_retries + 1,
                    e,
                )
                if retry_count < max_retries:
                    import asyncio
                    wait_time = 2 ** (retry_count + 1)  # Exponential backoff
                    _LOGGER.info("Waiting %d seconds before retry...", wait_time)
                    await asyncio.sleep(wait_time)
                    retry_count += 1
                    continue
                else:
                    _LOGGER.error("Network error persisted after all retries")
                    return

        _LOGGER.error("Failed to send SMS after all retry attempts")
