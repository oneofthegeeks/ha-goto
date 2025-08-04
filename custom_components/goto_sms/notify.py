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

        # Run the SMS sending in a thread to avoid blocking
        await self.hass.async_add_executor_job(
            self._send_sms, rendered_message, target, sender_id
        )

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

        # Run the SMS sending in a thread to avoid blocking
        await self.hass.async_add_executor_job(
            self._send_sms, rendered_message, target, sender_id
        )

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

    def _send_sms(self, message: str, target: str, sender_id: str) -> None:
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
                headers = self.oauth_manager.get_headers()
                if not headers:
                    _LOGGER.error("Failed to get valid authentication headers")
                    _LOGGER.error(
                        "This may indicate expired tokens or configuration issues"
                    )
                    _LOGGER.error("Re-authentication has been triggered automatically")
                    _LOGGER.error(
                        "Please check your Home Assistant UI for re-authentication prompts"
                    )
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

                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=30,
                )

                if response.status_code in [200, 201]:
                    _LOGGER.info("SMS sent successfully to %s", target)

                    # Track the message using both methods - schedule async tracking
                    self.hass.async_create_task(self._async_track_message_sent())
                    return  # Success, exit the retry loop

                elif response.status_code == 401:
                    _LOGGER.warning(
                        "Authentication failed (attempt %d/%d). Token may be expired.",
                        retry_count + 1,
                        max_retries + 1,
                    )

                    if retry_count < max_retries:
                        _LOGGER.info("Attempting to refresh tokens and retry...")
                        if self.oauth_manager.refresh_tokens():
                            _LOGGER.info(
                                "Token refresh successful, retrying SMS send..."
                            )
                            retry_count += 1
                            continue  # Retry with fresh tokens
                        else:
                            _LOGGER.error("Token refresh failed")
                            break  # Don't retry if refresh failed
                    else:
                        _LOGGER.error("All authentication attempts failed")
                        _LOGGER.error(
                            "Re-authentication has been triggered automatically"
                        )
                        _LOGGER.error(
                            "Please check your Home Assistant UI for re-authentication prompts"
                        )
                        return

                elif response.status_code == 429:  # Rate limited
                    _LOGGER.warning(
                        "Rate limited by GoTo API (attempt %d/%d)",
                        retry_count + 1,
                        max_retries + 1,
                    )
                    if retry_count < max_retries:
                        import time

                        wait_time = 2 ** (
                            retry_count + 1
                        )  # Exponential backoff: 2s, 4s
                        _LOGGER.info("Waiting %d seconds before retry...", wait_time)
                        time.sleep(wait_time)
                        retry_count += 1
                        continue
                    else:
                        _LOGGER.error("Rate limit exceeded after all retries")
                        return

                else:
                    _LOGGER.error(
                        "Failed to send SMS. Status: %d, Response: %s",
                        response.status_code,
                        response.text,
                    )
                    # For other errors, don't retry unless it's a network issue
                    break

            except requests.exceptions.RequestException as e:
                _LOGGER.error(
                    "Network error while sending SMS (attempt %d/%d): %s",
                    retry_count + 1,
                    max_retries + 1,
                    e,
                )
                if retry_count < max_retries:
                    import time

                    wait_time = 2 ** (retry_count + 1)  # Exponential backoff
                    _LOGGER.info("Waiting %d seconds before retry...", wait_time)
                    time.sleep(wait_time)
                    retry_count += 1
                    continue
                else:
                    _LOGGER.error("Network error persisted after all retries")
                    return

            except Exception as e:
                _LOGGER.error(
                    "Unexpected error while sending SMS (attempt %d/%d): %s",
                    retry_count + 1,
                    max_retries + 1,
                    e,
                )
                break  # Don't retry for unexpected errors

        _LOGGER.error("Failed to send SMS after all retry attempts")

    async def _async_track_message_sent(self) -> None:
        """Track that a message was sent using both tracking methods."""
        try:
            # Method 1: Update input_number if it exists
            try:
                current_count = self._get_input_number_count()
                if current_count is not None:
                    # Call the service directly since we're already in async context
                    await self.hass.services.async_call(
                        "input_number",
                        "set_value",
                        {
                            "entity_id": "input_number.sms_messages_sent",
                            "value": current_count + 1,
                        },
                    )
                    _LOGGER.info("Updated input_number SMS counter")
            except Exception as e:
                _LOGGER.error(f"Failed to update input_number counter: {e}")

            # Method 2: Update sensor if it exists
            try:
                sensor_entity_id = self._find_sms_sensor()
                if sensor_entity_id:
                    # Update the sensor state directly since we're already in async context
                    await self.hass.states.async_set(
                        sensor_entity_id,
                        self._get_sensor_current_value(sensor_entity_id) + 1,
                        {
                            "daily_count": self._get_sensor_attr(
                                sensor_entity_id, "daily_count", 0
                            )
                            + 1,
                            "weekly_count": self._get_sensor_attr(
                                sensor_entity_id, "weekly_count", 0
                            )
                            + 1,
                            "monthly_count": self._get_sensor_attr(
                                sensor_entity_id, "monthly_count", 0
                            )
                            + 1,
                            "total_count": self._get_sensor_attr(
                                sensor_entity_id, "total_count", 0
                            )
                            + 1,
                            "last_reset": datetime.now().date().isoformat(),
                        },
                    )
                    _LOGGER.info("Updated SMS sensor counter")
            except Exception as e:
                _LOGGER.error(f"Failed to update SMS sensor counter: {e}")

        except Exception as e:
            _LOGGER.error(f"Failed to track message: {e}")

    def _get_input_number_count(self) -> Optional[int]:
        """Get the current SMS count from the input_number entity."""
        try:
            state = self.hass.states.get("input_number.sms_messages_sent")
            if state and state.state:
                return int(float(state.state))
        except (ValueError, AttributeError):
            pass
        return None

    def _find_sms_sensor(self) -> Optional[str]:
        """Find the SMS counter sensor entity ID."""
        try:
            for entity_id in self.hass.states.async_entity_ids("sensor"):
                if "sms_messages_sent" in entity_id.lower():
                    return entity_id
        except Exception:
            pass
        return None

    def _get_sensor_current_value(self, entity_id: str) -> int:
        """Get the current value of a sensor."""
        try:
            state = self.hass.states.get(entity_id)
            if state and state.state:
                return int(float(state.state))
        except (ValueError, AttributeError):
            pass
        return 0

    def _get_sensor_attr(self, entity_id: str, attr: str, default: int = 0) -> int:
        """Get a specific attribute from a sensor."""
        try:
            state = self.hass.states.get(entity_id)
            if state and state.attributes:
                return int(state.attributes.get(attr, default))
        except (ValueError, AttributeError):
            pass
        return default
