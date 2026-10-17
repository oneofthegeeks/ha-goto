"""goto_sms.send_sms behaviour (v1-compatible call shape)."""
import pytest
from gotoconnect import GoToApiError, GoToAuthError, GoToError
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError

from custom_components.goto_sms.const import DOMAIN

BASE = {"message": "hi", "target": "+15550001111", "sender_id": "+15552223333"}


async def send(hass, **overrides):
    return await hass.services.async_call(
        DOMAIN, "send_sms", {**BASE, **overrides}, blocking=True, return_response=True
    )


async def test_happy_path_returns_response(hass: HomeAssistant, setup_entry, messaging) -> None:
    assert await send(hass) == {"id": "msg-1"}
    messaging.async_send_sms.assert_awaited_once_with(
        "+15552223333", ["+15550001111"], "hi"
    )


async def test_send_sms_tolerates_extra_keys(hass: HomeAssistant, setup_entry, messaging) -> None:
    """v1 ignored unknown keys (e.g. a pasted notify `title:`)."""
    assert await send(hass, title="ignored") == {"id": "msg-1"}


async def test_template_with_data_vars(hass: HomeAssistant, setup_entry, messaging) -> None:
    await send(hass, message="Hello {{ name }} in {{ room }}", data={"name": "Jo", "room": "kitchen"})
    assert messaging.async_send_sms.await_args.args[2] == "Hello Jo in kitchen"


async def test_template_with_state(hass: HomeAssistant, setup_entry, messaging) -> None:
    hass.states.async_set("sensor.t", "72")
    await send(hass, message="T={{ states('sensor.t') }}")
    assert messaging.async_send_sms.await_args.args[2] == "T=72"


async def test_bad_template_sends_original(hass: HomeAssistant, setup_entry, messaging) -> None:
    """v1 fell back to the raw message when rendering failed."""
    await send(hass, message="x {{ 1/0 }} y")
    assert messaging.async_send_sms.await_args.args[2] == "x {{ 1/0 }} y"


async def test_v1_schema_requires_sender_id(hass: HomeAssistant, setup_entry) -> None:
    import voluptuous as vol

    with pytest.raises(vol.Invalid):
        await hass.services.async_call(
            DOMAIN, "send_sms", {"message": "m", "target": "+1"}, blocking=True
        )


async def test_owner_equals_target(hass: HomeAssistant, setup_entry, messaging) -> None:
    with pytest.raises(ServiceValidationError):
        await send(hass, target=BASE["sender_id"])
    messaging.async_send_sms.assert_not_awaited()


async def test_auth_error_starts_reauth(hass: HomeAssistant, setup_entry, messaging) -> None:
    messaging.async_send_sms.side_effect = GoToAuthError("no")
    with pytest.raises(HomeAssistantError):
        await send(hass)
    await hass.async_block_till_done()
    assert any(
        f["context"]["source"] == "reauth"
        for f in hass.config_entries.flow.async_progress()
    )


async def test_api_error_includes_status(hass: HomeAssistant, setup_entry, messaging) -> None:
    messaging.async_send_sms.side_effect = GoToApiError("bad", 429)
    with pytest.raises(HomeAssistantError, match="429"):
        await send(hass)


async def test_generic_error(hass: HomeAssistant, setup_entry, messaging) -> None:
    messaging.async_send_sms.side_effect = GoToError("boom")
    with pytest.raises(HomeAssistantError):
        await send(hass)


async def test_not_loaded(hass: HomeAssistant, setup_entry) -> None:
    await hass.config_entries.async_unload(setup_entry.entry_id)
    with pytest.raises(ServiceValidationError):
        await send(hass)
