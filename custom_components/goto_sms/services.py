"""goto_sms.send_sms action; the legacy notify shim reuses async_send_sms."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from gotoconnect import GoToApiError, GoToAuthError, GoToError
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.template import Template, TemplateError

from .const import (
    ATTR_MESSAGE,
    ATTR_SENDER_ID,
    ATTR_TARGET,
    ATTR_TEMPLATE_DATA,
    DOMAIN,
    SERVICE_SEND_SMS,
)

_LOGGER = logging.getLogger(__name__)

# Identical to v1: message/target/sender_id required, data optional.
SEND_SMS_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_MESSAGE): cv.string,
        vol.Required(ATTR_TARGET): cv.string,
        vol.Required(ATTR_SENDER_ID): cv.string,
        vol.Optional(ATTR_TEMPLATE_DATA, default=dict): dict,
    }
)


def _render(hass: HomeAssistant, message: str, variables: dict[str, Any]) -> str:
    """Render HA templates in the message; on failure send it unrendered (v1 behaviour)."""
    if "{{" not in message or "}}" not in message:
        return message
    try:
        return str(Template(message, hass).async_render(variables, parse_result=False))
    except TemplateError as err:
        _LOGGER.error("Template rendering failed: %s", err)
        return message


async def async_send_sms(
    hass: HomeAssistant,
    message: str,
    targets: list[str],
    sender_id: str,
    data: dict[str, Any] | None = None,
) -> dict:
    """Render and send one SMS through the loaded config entry."""
    entry = next(
        (
            e
            for e in hass.config_entries.async_entries(DOMAIN)
            if e.state is ConfigEntryState.LOADED
        ),
        None,
    )
    if entry is None:
        raise ServiceValidationError("GoTo SMS is not set up or not loaded")
    if sender_id in targets:
        raise ServiceValidationError("sender_id and target must be different numbers")

    body = _render(hass, message, data or {})
    try:
        return await entry.runtime_data.messaging.async_send_sms(
            sender_id, targets, body
        )
    except GoToAuthError as err:
        entry.async_start_reauth(hass)
        raise HomeAssistantError("GoTo rejected the credentials; reauthenticate") from err
    except GoToApiError as err:
        raise HomeAssistantError(f"GoTo API error (HTTP {err.status})") from err
    except GoToError as err:
        raise HomeAssistantError(f"Sending SMS failed: {err}") from err


def async_setup_services(hass: HomeAssistant) -> None:
    """Register goto_sms.send_sms (once, in async_setup)."""

    async def _send_sms(call: ServiceCall) -> ServiceResponse:
        return await async_send_sms(
            hass,
            call.data[ATTR_MESSAGE],
            [call.data[ATTR_TARGET]],
            call.data[ATTR_SENDER_ID],
            call.data[ATTR_TEMPLATE_DATA],
        )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_SMS,
        _send_sms,
        schema=SEND_SMS_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
