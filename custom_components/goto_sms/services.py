"""goto_sms.send_sms and call_tts actions; the legacy notify shim reuses async_send_sms."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from gotoconnect import (
    GoToApiError,
    GoToAuthError,
    GoToCallError,
    GoToError,
    GoToSipError,
    GoToVoice,
)
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.exceptions import (
    HomeAssistantError,
    ServiceValidationError,
    Unauthorized,
    UnknownUser,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.template import Template, TemplateError

from .const import (
    ATTR_LANGUAGE,
    ATTR_MESSAGE,
    ATTR_REPEAT,
    ATTR_RING_TIMEOUT,
    ATTR_SENDER_ID,
    ATTR_TARGET,
    ATTR_TEMPLATE_DATA,
    ATTR_TTS_ENGINE,
    CONF_SIP_PASSWORD,
    CONF_SIP_PROXY,
    CONF_SIP_SERVER,
    CONF_SIP_USERNAME,
    DEFAULT_SIP_SERVER,
    DOMAIN,
    SERVICE_CALL_TTS,
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
    },
    # v1 ignored unknown keys (e.g. a pasted notify `title:`); keep that.
    extra=vol.ALLOW_EXTRA,
)

CALL_TTS_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_TARGET): cv.string,
        vol.Required(ATTR_MESSAGE): cv.string,
        vol.Optional(ATTR_TTS_ENGINE): cv.string,
        vol.Optional(ATTR_LANGUAGE): cv.string,
        vol.Optional(ATTR_REPEAT, default=1): vol.All(vol.Coerce(int), vol.Range(1, 3)),
        vol.Optional(ATTR_RING_TIMEOUT, default=25): vol.All(
            vol.Coerce(int), vol.Range(5, 60)
        ),
    }
)

# 2025.1 has no tts.async_create_stream (added later); the media-source helpers
# are the public path to rendered bytes. The lib resamples any PCM WAV anyway.
PREFERRED_8K_WAV = {
    "preferred_format": "wav",
    "preferred_sample_rate": 8000,
    "preferred_sample_channels": 1,
    "preferred_sample_bytes": 2,
}


def _render(
    hass: HomeAssistant, message: str, variables: dict[str, Any], strict: bool = False
) -> str:
    """Render HA templates in the message.

    SMS (strict=False) falls back to the raw text on failure (v1 behaviour); a
    voice call must never read raw template syntax aloud, so strict raises.
    """
    if "{{" not in message or "}}" not in message:
        return message
    try:
        return str(Template(message, hass).async_render(variables, parse_result=False))
    except TemplateError as err:
        _LOGGER.error("Template rendering failed: %s", err)
        if strict:
            raise ServiceValidationError(f"Message template failed to render: {err}") from err
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


async def _synthesize(
    hass: HomeAssistant, text: str, engine: str | None, language: str | None
) -> bytes:
    """Render text through a TTS engine to WAV bytes (8 kHz mono preferred)."""
    # tts is only an after_dependency (its pip requirements may not be installed
    # unless the user set it up), so import lazily.
    if "tts" not in hass.config.components:
        raise ServiceValidationError("No text-to-speech engine is available")
    from homeassistant.components import tts
    from homeassistant.components.tts.media_source import generate_media_source_id

    resolved = tts.async_resolve_engine(hass, engine)
    if resolved is None:
        if engine:
            raise ServiceValidationError(f"Unknown text-to-speech engine: {engine}")
        raise ServiceValidationError("No text-to-speech engine is available")
    try:
        # Only validates language/options against the engine; no audio yet.
        source_id = generate_media_source_id(
            hass, text, resolved, language, dict(PREFERRED_8K_WAV)
        )
    except HomeAssistantError as err:
        if language:
            raise ServiceValidationError(
                f"Language '{language}' is not supported by {resolved}"
            ) from err
        raise HomeAssistantError(f"Text-to-speech failed: {err}") from err
    try:
        extension, audio = await tts.async_get_media_source_audio(hass, source_id)
    except HomeAssistantError as err:
        raise HomeAssistantError(f"Text-to-speech failed: {err}") from err
    if extension != "wav":
        raise HomeAssistantError(f"TTS engine returned {extension}, expected wav")
    return audio


async def async_call_tts(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Render the message and phone it to the target."""
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
    opts = entry.options
    if not (opts.get(CONF_SIP_USERNAME) and opts.get(CONF_SIP_PASSWORD)):
        raise ServiceValidationError(
            "Voice calls are not configured; add SIP details in the integration options",
            translation_domain=DOMAIN,
            translation_key="sip_not_configured",
        )

    text = _render(hass, data[ATTR_MESSAGE], {}, strict=True)
    wav = await _synthesize(hass, text, data.get(ATTR_TTS_ENGINE), data.get(ATTR_LANGUAGE))

    # Fresh instance per call: GoToVoice holds per-call SIP state.
    voice = GoToVoice(
        opts[CONF_SIP_USERNAME],
        opts[CONF_SIP_PASSWORD],
        server=opts.get(CONF_SIP_SERVER) or DEFAULT_SIP_SERVER,
        proxy=opts.get(CONF_SIP_PROXY) or None,
    )
    try:
        result = await voice.call_and_play(
            data[ATTR_TARGET],
            wav,
            ring_timeout=data[ATTR_RING_TIMEOUT],
            repeat=data[ATTR_REPEAT],
        )
    except GoToAuthError as err:
        raise ServiceValidationError(
            "GoTo rejected the SIP credentials; check them in the integration options"
        ) from err
    except ValueError as err:  # bad number / unusable WAV
        raise ServiceValidationError(str(err)) from err
    except (GoToSipError, GoToCallError, GoToError) as err:
        raise HomeAssistantError(f"Voice call failed: {err}") from err
    return {
        "answered": result.answered,
        "duration": result.duration,
        "reason": result.reason,
        "bye_confirmed": result.bye_confirmed,
    }


def async_setup_services(hass: HomeAssistant) -> None:
    """Register goto_sms.send_sms + call_tts (once, in async_setup)."""

    async def _send_sms(call: ServiceCall) -> ServiceResponse:
        return await async_send_sms(
            hass,
            call.data[ATTR_MESSAGE],
            [call.data[ATTR_TARGET]],
            call.data[ATTR_SENDER_ID],
            call.data[ATTR_TEMPLATE_DATA],
        )

    async def _call_tts(call: ServiceCall) -> ServiceResponse:
        # This dials real phones, so admin-only. Same check as
        # helpers.service.async_register_admin_service, which can't return a
        # response in HA 2025.1. No user_id (automations) is allowed.
        if call.context.user_id:
            user = await hass.auth.async_get_user(call.context.user_id)
            if user is None:
                raise UnknownUser(context=call.context)
            if not user.is_admin:
                raise Unauthorized(context=call.context)
        return await async_call_tts(hass, dict(call.data))

    hass.services.async_register(
        DOMAIN,
        SERVICE_CALL_TTS,
        _call_tts,
        schema=CALL_TTS_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_SMS,
        _send_sms,
        schema=SEND_SMS_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
