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
        try:
            _LOGGER.debug("Attempting to get authentication headers")
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

                # Track the message using both methods
                self._track_message_sent()

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
                        if response.status_code in [200, 201]:
                            _LOGGER.info("SMS sent successfully after token refresh")

                            # Track the message using both methods
                            self._track_message_sent()

                            return

                _LOGGER.error("Failed to send SMS after token refresh")
                _LOGGER.error("Re-authentication has been triggered automatically")
                _LOGGER.error(
                    "Please check your Home Assistant UI for re-authentication prompts"
                )
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

    def _track_message_sent(self) -> None:
        """Track that a message was sent using both tracking methods."""
        try:
            # Method 1: Update input_number if it exists
            try:
                current_count = self._get_input_number_count()
                if current_count is not None:
                    self.hass.async_create_task(
                        self.hass.services.async_call(
                            "input_number",
                            "set_value",
                            {
                                "entity_id": "input_number.sms_messages_sent",
                                "value": current_count + 1,
                            },
                        )
                    )
                    _LOGGER.debug("Updated input_number SMS counter")
            except Exception as e:
                _LOGGER.debug(f"Failed to update input_number counter: {e}")

            # Method 2: Update sensor if it exists
            try:
                sensor_entity_id = self._find_sms_sensor()
                if sensor_entity_id:
                    # Get the sensor entity and increment it
                    sensor_state = self.hass.states.get(sensor_entity_id)
                    if sensor_state:
                        # Try to find the sensor object in the entity registry
                        entity_registry = self.hass.data.get("entity_registry")
                        if entity_registry:
                            for entity in entity_registry.entities.values():
                                if entity.entity_id == sensor_entity_id:
                                    if hasattr(entity, "increment_counter"):
                                        entity.increment_counter()
                                        entity.save_state()
                                        _LOGGER.debug("Updated SMS sensor counter")
                                        break
            except Exception as e:
                _LOGGER.debug(f"Failed to update SMS sensor counter: {e}")

        except Exception as e:
            _LOGGER.debug(f"Failed to track message: {e}")

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
