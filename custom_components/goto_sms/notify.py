"""Legacy notify.goto_sms shim; delegates to the send_sms code path."""

from __future__ import annotations

from typing import Any

from homeassistant.components.notify import ATTR_TARGET, BaseNotificationService
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import ATTR_SENDER_ID
from .services import async_send_sms


async def async_get_service(
    hass: HomeAssistant,
    config: ConfigType,
    discovery_info: DiscoveryInfoType | None = None,
) -> BaseNotificationService:
    """Return the shim (loaded via discovery from async_setup_entry)."""
    return GoToNotificationService()


class GoToNotificationService(BaseNotificationService):
    """notify.goto_sms: target list + data.sender_id; other data keys are template vars."""

    async def async_send_message(self, message: str, **kwargs: Any) -> None:
        """Send via the same path as goto_sms.send_sms."""
        data = dict(kwargs.get("data") or {})
        sender_id = data.pop(ATTR_SENDER_ID, None)
        targets = kwargs.get(ATTR_TARGET)
        if not sender_id or not targets:
            raise ServiceValidationError(
                "notify.goto_sms needs a target and data.sender_id (E.164 GoTo number)"
            )
        await async_send_sms(self.hass, message, list(targets), sender_id, data)
