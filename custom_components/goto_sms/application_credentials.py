"""Application credentials platform for GoTo SMS."""

from __future__ import annotations

import logging
from json import JSONDecodeError
from typing import cast

from aiohttp import BasicAuth, ClientError
from homeassistant.components.application_credentials import (
    AuthImplementation,
    AuthorizationServer,
    ClientCredential,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import OAUTH2_AUTHORIZE_URL, OAUTH2_TOKEN_URL, OAUTH_SCOPES

_LOGGER = logging.getLogger(__name__)


async def async_get_authorization_server(hass: HomeAssistant) -> AuthorizationServer:
    """Return GoTo's OAuth endpoints."""
    return AuthorizationServer(OAUTH2_AUTHORIZE_URL, OAUTH2_TOKEN_URL)


class GoToBasicAuthImplementation(AuthImplementation):
    """OAuth2 implementation that sends client creds as HTTP Basic auth.

    HA's default puts client_id/client_secret in the POST body; GoTo's token
    endpoint is proven to accept them in the Authorization header instead.
    """

    @property
    def extra_authorize_data(self) -> dict:
        """Request the SMS scope on the authorize URL."""
        return {"scope": " ".join(OAUTH_SCOPES)}

    async def _token_request(self, data: dict) -> dict:
        """POST to the token endpoint with Basic auth and no creds in the body."""
        # Base class adds client_id to refresh bodies; creds ride the header only.
        data = {k: v for k, v in data.items() if k not in ("client_id", "client_secret")}
        session = async_get_clientsession(self.hass)
        _LOGGER.debug("Sending token request to %s", self.token_url)
        resp = await session.post(
            self.token_url,
            data=data,
            headers={
                "Authorization": BasicAuth(self.client_id, self.client_secret or "").encode()
            },
        )
        if resp.status >= 400:
            try:
                error_response = await resp.json()
            except (ClientError, JSONDecodeError):
                error_response = {}
            _LOGGER.error(
                "Token request for %s failed (%s): %s",
                self.domain,
                error_response.get("error", "unknown"),
                error_response.get("error_description", "unknown error"),
            )
        resp.raise_for_status()
        return cast(dict, await resp.json())


async def async_get_auth_implementation(
    hass: HomeAssistant, auth_domain: str, credential: ClientCredential
) -> config_entry_oauth2_flow.AbstractOAuth2Implementation:
    """Return the Basic-auth implementation."""
    return GoToBasicAuthImplementation(
        hass, auth_domain, credential, await async_get_authorization_server(hass)
    )


async def async_get_description_placeholders(hass: HomeAssistant) -> dict[str, str]:
    """Placeholders for the credentials dialog (hassfest forbids URLs in strings)."""
    return {"redirect_url": "https://my.home-assistant.io/redirect/oauth"}
