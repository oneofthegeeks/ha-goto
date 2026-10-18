"""Legacy notify.goto_sms shim shares the send_sms code path."""
import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError


async def notify(hass, **data):
    await hass.services.async_call(
        "notify", "goto_sms", {"message": "hi", "target": ["+15550001111"], **data}, blocking=True
    )


async def test_notify_sends(hass: HomeAssistant, setup_entry, messaging) -> None:
    await notify(hass, data={"sender_id": "+15552223333"})
    messaging.async_send_sms.assert_awaited_once_with(
        "+15552223333", ["+15550001111"], "hi"
    )


async def test_notify_template_uses_remaining_data(hass: HomeAssistant, setup_entry, messaging) -> None:
    await notify(hass, message="{{ n }}!", data={"sender_id": "+15552223333", "n": "yo"})
    assert messaging.async_send_sms.await_args.args[2] == "yo!"


async def test_notify_requires_sender_and_target(hass: HomeAssistant, setup_entry, messaging) -> None:
    with pytest.raises(ServiceValidationError):
        await notify(hass)
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            "notify", "goto_sms", {"message": "hi", "data": {"sender_id": "+1"}}, blocking=True
        )
    messaging.async_send_sms.assert_not_awaited()
