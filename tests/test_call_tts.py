"""goto_sms.call_tts and the SIP options flow."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from gotoconnect import CallResult, GoToAuthError, GoToCallError, GoToSipError
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError

from custom_components.goto_sms.const import DOMAIN

SIP = {
    "sip_username": "u",
    "sip_password": "p",
    "sip_server": "reg.jiveip.net",
    "sip_proxy": "acct.jive.rtcfront.net",
}
BASE = {"target": "+15550001111", "message": "Door open {{ 1 + 1 }}"}


@pytest.fixture
def voice():
    """Patch GoToVoice at the integration boundary."""
    inst = MagicMock()
    inst.call_and_play = AsyncMock(
        return_value=CallResult(answered=True, duration=4.5, reason="completed", bye_confirmed=True)
    )
    with patch("custom_components.goto_sms.services.GoToVoice", return_value=inst) as cls:
        inst.cls = cls
        yield inst


@pytest.fixture
def synth():
    with patch(
        "custom_components.goto_sms.services._synthesize", AsyncMock(return_value=b"RIFFwav")
    ) as m:
        yield m


async def call(hass, **extra):
    return await hass.services.async_call(
        DOMAIN, "call_tts", {**BASE, **extra}, blocking=True, return_response=True
    )


async def test_happy_path(hass: HomeAssistant, setup_entry, voice, synth) -> None:
    hass.config_entries.async_update_entry(setup_entry, options=SIP)
    result = await call(hass, repeat=2, ring_timeout=30, language="en-US", tts_engine="tts.x")
    assert result == {"answered": True, "duration": 4.5, "reason": "completed", "bye_confirmed": True}
    synth.assert_awaited_once_with(hass, "Door open 2", "tts.x", "en-US")
    voice.cls.assert_called_once_with(
        "u", "p", server="reg.jiveip.net", proxy="acct.jive.rtcfront.net"
    )
    voice.call_and_play.assert_awaited_once_with(
        "+15550001111", b"RIFFwav", ring_timeout=30, repeat=2
    )


async def test_defaults(hass: HomeAssistant, setup_entry, voice, synth) -> None:
    hass.config_entries.async_update_entry(setup_entry, options={"sip_username": "u", "sip_password": "p"})
    await call(hass)
    voice.cls.assert_called_once_with("u", "p", server="reg.jiveip.net", proxy=None)
    assert voice.call_and_play.await_args.kwargs == {"ring_timeout": 25, "repeat": 1}


async def test_sip_not_configured(hass: HomeAssistant, setup_entry, voice, synth) -> None:
    with pytest.raises(ServiceValidationError):
        await call(hass)
    voice.cls.assert_not_called()


async def test_no_tts_engine(hass: HomeAssistant, setup_entry, voice) -> None:
    hass.config_entries.async_update_entry(setup_entry, options=SIP)
    with pytest.raises(ServiceValidationError):
        await call(hass)
    voice.cls.assert_not_called()


async def test_sip_auth_error(hass: HomeAssistant, setup_entry, voice, synth) -> None:
    hass.config_entries.async_update_entry(setup_entry, options=SIP)
    voice.call_and_play.side_effect = GoToAuthError("bad")
    with pytest.raises(ServiceValidationError):
        await call(hass)


@pytest.mark.parametrize("exc", [GoToSipError("x"), GoToCallError("x")])
async def test_sip_failures(hass: HomeAssistant, setup_entry, voice, synth, exc) -> None:
    hass.config_entries.async_update_entry(setup_entry, options=SIP)
    voice.call_and_play.side_effect = exc
    with pytest.raises(HomeAssistantError) as err:
        await call(hass)
    assert not isinstance(err.value, ServiceValidationError)


async def test_bad_number(hass: HomeAssistant, setup_entry, voice, synth) -> None:
    hass.config_entries.async_update_entry(setup_entry, options=SIP)
    voice.call_and_play.side_effect = ValueError("bad number")
    with pytest.raises(ServiceValidationError):
        await call(hass)


async def test_synthesize_uses_8k_wav(hass: HomeAssistant) -> None:
    from homeassistant.components import tts

    from custom_components.goto_sms import services

    hass.config.components.add("tts")
    with patch.object(tts, "async_resolve_engine", return_value="tts.x"), patch(
        "homeassistant.components.tts.media_source.generate_media_source_id", return_value="id"
    ) as gen, patch.object(
        tts, "async_get_media_source_audio", AsyncMock(return_value=("wav", b"W"))
    ):
        assert await services._synthesize(hass, "hi", None, "en") == b"W"
    assert gen.call_args.args[4] == {
        "preferred_format": "wav",
        "preferred_sample_rate": 8000,
        "preferred_sample_channels": 1,
        "preferred_sample_bytes": 2,
    }


# ---- options flow ----
async def test_options_flow_saves_sip(hass: HomeAssistant, setup_entry) -> None:
    res = await hass.config_entries.options.async_init(setup_entry.entry_id)
    assert res["type"] == "form"
    res = await hass.config_entries.options.async_configure(
        res["flow_id"],
        {"sip_username": "u", "sip_password": "p", "sip_server": "s.example", "sip_proxy": "px"},
    )
    assert res["type"] == "create_entry"
    assert setup_entry.options == {
        "sip_username": "u", "sip_password": "p", "sip_server": "s.example", "sip_proxy": "px",
    }


async def test_options_flow_incomplete_and_clear(hass: HomeAssistant, setup_entry) -> None:
    res = await hass.config_entries.options.async_init(setup_entry.entry_id)
    res = await hass.config_entries.options.async_configure(res["flow_id"], {"sip_username": "u"})
    assert res["type"] == "form" and res["errors"] == {"base": "sip_incomplete"}
    res = await hass.config_entries.options.async_configure(res["flow_id"], {})
    assert res["type"] == "create_entry"
    assert setup_entry.options == {}
