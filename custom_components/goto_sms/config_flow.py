"""Config flow for GoTo SMS integration."""

import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    DOMAIN,
    OAUTH2_AUTHORIZE_URL,
    OAUTH2_SCOPE,
    OAUTH2_TOKEN_URL,
)
from .oauth import GoToOAuth2Manager

_LOGGER = logging.getLogger(__name__)


class GoToSMSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GoTo SMS."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        _LOGGER.info("Initializing GoTo SMS config flow")
        self.oauth_manager: Optional[GoToOAuth2Manager] = None
        self.client_id: Optional[str] = None
        self.client_secret: Optional[str] = None

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        _LOGGER.info(
            "GoTo SMS config flow user step called, user_input: %s",
            user_input is not None,
        )
        errors = {}

        if user_input is not None:
            self.client_id = user_input[CONF_CLIENT_ID]
            self.client_secret = user_input[CONF_CLIENT_SECRET]

            # Validate credentials by attempting to create OAuth manager
            try:
                _LOGGER.info(
                    "Creating OAuth manager with client_id: %s", self.client_id
                )
                # For config flow, we need to create a temporary OAuth manager
                # that doesn't require a config entry yet
                self.oauth_manager = GoToOAuth2Manager(
                    self.hass, None  # No config entry during setup
                )
                # Set the credentials manually for the setup process
                self.oauth_manager.client_id = self.client_id
                self.oauth_manager.client_secret = self.client_secret
                _LOGGER.info("OAuth manager created successfully")
                return await self.async_step_oauth()
            except Exception as e:
                _LOGGER.error("Failed to initialize OAuth manager: %s", e)
                errors["base"] = "invalid_credentials"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_CLIENT_ID): str,
                    vol.Required(CONF_CLIENT_SECRET): str,
                }
            ),
            errors=errors,
        )

    async def async_step_oauth(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the OAuth2 authorization step."""
        _LOGGER.info("Entering OAuth step, user_input: %s", user_input is not None)
        if user_input is not None:
            # Handle the OAuth2 callback
            try:
                authorization_response = user_input.get("authorization_response")
                if not authorization_response:
                    raise HomeAssistantError("No authorization response received")

                success = await self.hass.async_add_executor_job(
                    self.oauth_manager.fetch_token, authorization_response
                )

                if success:
                    # Create the config entry with tokens
                    config_data = {
                        CONF_CLIENT_ID: self.client_id,
                        CONF_CLIENT_SECRET: self.client_secret,
                        "tokens": self.oauth_manager._tokens,  # Include the tokens
                    }

                    return self.async_create_entry(
                        title="GoTo SMS",
                        data=config_data,
                    )
                else:
                    return self.async_show_form(
                        step_id="oauth",
                        errors={"base": "oauth_failed"},
                    )

            except Exception as e:
                _LOGGER.error("OAuth2 flow failed: %s", e)
                return self.async_show_form(
                    step_id="oauth",
                    errors={"base": "oauth_failed"},
                )

        # Get the authorization URL
        try:
            _LOGGER.info("About to generate authorization URL")
            auth_url = self.oauth_manager.get_authorization_url()
            _LOGGER.info("Generated authorization URL: %s", auth_url)
        except Exception as e:
            _LOGGER.error("Failed to generate authorization URL: %s", e)
            # Create a fallback URL manually
            auth_url = (
                f"https://authentication.logmeininc.com/oauth/authorize"
                f"?client_id={self.client_id}"
                f"&redirect_uri=https://home-assistant.io/auth/callback"
                f"&response_type=code&scope={OAUTH2_SCOPE}"
            )
            _LOGGER.info("Using fallback authorization URL: %s", auth_url)

        _LOGGER.info("Showing OAuth form with auth_url: %s", auth_url)
        # Create a simpler form that shows the URL directly
        description = f"""
Please authorize the application by visiting this URL:

**{auth_url}**

After authorization, you'll be redirected to a URL like:
`https://home-assistant.io/auth/callback?code=AUTHORIZATION_CODE`

Copy the entire URL and paste it below.

**Note:** If you only see an authorization code (without the full URL), you can paste just the code.
        """

        return self.async_show_form(
            step_id="oauth",
            description_placeholders={
                "auth_url": auth_url,
                "client_id": self.client_id,
            },
            data_schema=vol.Schema(
                {
                    vol.Required("authorization_response"): str,
                }
            ),
        )

    async def async_step_reauth(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle re-authentication."""
        _LOGGER.info("Starting re-authentication flow")
        
        # Get the existing config entry
        config_entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        if not config_entry:
            _LOGGER.error("No config entry found for re-authentication")
            return self.async_abort(reason="unknown")
        
        # Store the existing credentials
        self.client_id = config_entry.data[CONF_CLIENT_ID]
        self.client_secret = config_entry.data[CONF_CLIENT_SECRET]
        
        # Create OAuth manager with existing credentials
        self.oauth_manager = GoToOAuth2Manager(self.hass, config_entry)
        self.oauth_manager.client_id = self.client_id
        self.oauth_manager.client_secret = self.client_secret
        
        return await self.async_step_reauth_oauth()

    async def async_step_reauth_oauth(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the re-authentication OAuth step."""
        _LOGGER.info("Entering re-authentication OAuth step")
        
        if user_input is not None:
            # Handle the OAuth2 callback
            try:
                authorization_response = user_input.get("authorization_response")
                if not authorization_response:
                    raise HomeAssistantError("No authorization response received")

                success = await self.hass.async_add_executor_job(
                    self.oauth_manager.fetch_token, authorization_response
                )

                if success:
                    # Update the existing config entry with new tokens
                    config_entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
                    if config_entry:
                        # Update the config entry with new tokens
                        new_data = dict(config_entry.data)
                        new_data["tokens"] = self.oauth_manager._tokens
                        
                        self.hass.config_entries.async_update_entry(
                            config_entry, data=new_data
                        )
                        
                        _LOGGER.info("Re-authentication successful")
                        return self.async_abort(reason="reauth_successful")
                    else:
                        _LOGGER.error("Config entry not found during re-authentication")
                        return self.async_abort(reason="unknown")
                else:
                    return self.async_show_form(
                        step_id="reauth_oauth",
                        errors={"base": "oauth_failed"},
                    )

            except Exception as e:
                _LOGGER.error("Re-authentication OAuth2 flow failed: %s", e)
                return self.async_show_form(
                    step_id="reauth_oauth",
                    errors={"base": "oauth_failed"},
                )

        # Get the authorization URL for re-authentication
        try:
            _LOGGER.info("Generating re-authentication authorization URL")
            auth_url = self.oauth_manager.get_authorization_url()
            _LOGGER.info("Generated re-authentication authorization URL: %s", auth_url)
        except Exception as e:
            _LOGGER.error("Failed to generate re-authentication authorization URL: %s", e)
            # Create a fallback URL manually
            auth_url = (
                f"https://authentication.logmeininc.com/oauth/authorize"
                f"?client_id={self.client_id}"
                f"&redirect_uri=https://home-assistant.io/auth/callback"
                f"&response_type=code&scope={OAUTH2_SCOPE}"
            )
            _LOGGER.info("Using fallback re-authentication authorization URL: %s", auth_url)

        description = f"""
Your GoTo SMS integration needs to be re-authenticated.

Please authorize the application by visiting this URL:

**{auth_url}**

After authorization, you'll be redirected to a URL like:
`https://home-assistant.io/auth/callback?code=AUTHORIZATION_CODE`

Copy the entire URL and paste it below.

**Note:** If you only see an authorization code (without the full URL), you can paste just the code.
        """

        return self.async_show_form(
            step_id="reauth_oauth",
            description_placeholders={
                "auth_url": auth_url,
                "client_id": self.client_id,
            },
            data_schema=vol.Schema(
                {
                    vol.Required("authorization_response"): str,
                }
            ),
        )

    async def async_step_import(self, import_info: Dict[str, Any]) -> FlowResult:
        """Handle import from configuration.yaml."""
        return await self.async_step_user(import_info)


class InvalidCredentials(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class OAuth2Error(HomeAssistantError):
    """Error to indicate there is an OAuth2 error."""
