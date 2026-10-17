"""Options flow: optional SIP credentials for goto_sms.call_tts."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import OptionsFlow
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    CONF_SIP_PASSWORD,
    CONF_SIP_PROXY,
    CONF_SIP_SERVER,
    CONF_SIP_USERNAME,
    DEFAULT_SIP_SERVER,
)

_KEYS = (CONF_SIP_USERNAME, CONF_SIP_PASSWORD, CONF_SIP_SERVER, CONF_SIP_PROXY)


class GoToOptionsFlow(OptionsFlow):
    """Voice is optional: leave everything blank to disable call_tts."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        """Collect SIP username/password (a set) plus server and proxy."""
        errors: dict[str, str] = {}
        if user_input is not None:
            data = {k: v.strip() for k, v in user_input.items() if v and v.strip()}
            # The password is never sent to the frontend; blank keeps the stored one.
            if not data.get(CONF_SIP_PASSWORD) and data.get(CONF_SIP_USERNAME):
                stored = self.config_entry.options.get(CONF_SIP_PASSWORD)
                if stored:
                    data[CONF_SIP_PASSWORD] = stored
            if bool(data.get(CONF_SIP_USERNAME)) != bool(data.get(CONF_SIP_PASSWORD)):
                errors["base"] = "sip_incomplete"
            elif not data.get(CONF_SIP_USERNAME):
                return self.async_create_entry(data={})  # cleared: voice off
            else:
                data.setdefault(CONF_SIP_SERVER, DEFAULT_SIP_SERVER)
                return self.async_create_entry(data=data)

        text = TextSelector()
        schema = vol.Schema(
            {
                vol.Optional(CONF_SIP_USERNAME): text,
                vol.Optional(CONF_SIP_PASSWORD): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.PASSWORD)
                ),
                vol.Optional(CONF_SIP_SERVER, default=DEFAULT_SIP_SERVER): text,
                vol.Optional(CONF_SIP_PROXY): text,
            }
        )
        suggested = {
            k: (user_input or self.config_entry.options).get(k)
            for k in _KEYS
            if k != CONF_SIP_PASSWORD
        }
        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(schema, suggested),
            errors=errors,
        )
