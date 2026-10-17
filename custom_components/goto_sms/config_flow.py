"""Config flow for GoTo SMS (application-credentials OAuth2)."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from homeassistant.config_entries import SOURCE_REAUTH, ConfigEntry, ConfigFlowResult
from homeassistant.core import callback
from homeassistant.helpers import config_entry_oauth2_flow

from .const import DOMAIN
from .options_flow import GoToOptionsFlow


class GoToOAuthFlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    """Handle the OAuth2 config flow.

    The scope is added by GoToBasicAuthImplementation.extra_authorize_data;
    do NOT repeat it here or the authorize URL gets two scope params.
    """

    DOMAIN = DOMAIN
    # Task 4 (migration) depends on these exact numbers.
    VERSION = 2
    MINOR_VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> GoToOptionsFlow:
        """Options hold the optional SIP (voice) settings."""
        return GoToOptionsFlow()

    @property
    def logger(self) -> logging.Logger:
        """Return the flow logger."""
        return logging.getLogger(__name__)

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Start reauth when the refresh token is rejected."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask the user to re-authorize, then run the OAuth flow."""
        if user_input is None:
            return self.async_show_form(step_id="reauth_confirm")
        return await self.async_step_user()

    async def async_oauth_create_entry(self, data: dict[str, Any]) -> ConfigFlowResult:
        """Create the (single) entry, or refresh tokens on reauth."""
        # GoTo has no whoami in our scope, so the domain is the singleton id.
        await self.async_set_unique_id(DOMAIN)
        if self.source == SOURCE_REAUTH:
            self._abort_if_unique_id_mismatch()
            return self.async_update_reload_and_abort(
                self._get_reauth_entry(), data_updates=data
            )
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title="GoTo Connect", data=data)
