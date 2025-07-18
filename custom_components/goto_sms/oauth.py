"""OAuth2 token management for GoTo SMS integration."""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

# Allow HTTP for development (disable SSL verification warnings)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from .const import (
    OAUTH2_AUTHORIZE_URL,
    OAUTH2_TOKEN_URL,
    OAUTH2_SCOPE,
    CONF_ACCESS_TOKEN,
    CONF_REFRESH_TOKEN,
    CONF_TOKEN_EXPIRES_AT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class GoToOAuth2Manager:
    """Manages OAuth2 tokens for GoTo Connect API."""

    def __init__(self, hass: HomeAssistant, config_entry: Optional[ConfigEntry] = None):
        """Initialize the OAuth2 manager."""
        self.hass = hass
        self.config_entry = config_entry
        
        # Handle both config entry and manual credential setting
        if config_entry is not None:
            self.client_id = config_entry.data[CONF_CLIENT_ID]
            self.client_secret = config_entry.data[CONF_CLIENT_SECRET]
        else:
            # For config flow setup, credentials will be set manually
            self.client_id = None
            self.client_secret = None
        # Initialize session with client_id (will be set later if None)
        self.session = OAuth2Session(
            self.client_id or "temp",  # Use temp placeholder if None
            redirect_uri="https://home-assistant.io/auth/callback",
            scope=OAUTH2_SCOPE,
        )
        self._tokens = {}

    def load_tokens(self) -> bool:
        """Load tokens from config entry."""
        try:
            if self.config_entry is None:
                _LOGGER.warning("No config entry available for token loading")
                return False
                
            tokens = self.config_entry.data.get("tokens", {})
            if not tokens:
                _LOGGER.warning("No tokens found in config entry")
                return False

            self._tokens = tokens

            if not self._validate_tokens():
                _LOGGER.warning("Invalid or expired tokens found")
                return False

            _LOGGER.info("Tokens loaded successfully")
            return True

        except Exception as e:
            _LOGGER.error("Failed to load tokens: %s", e)
            return False

    def save_tokens(self) -> bool:
        """Save tokens to config entry."""
        try:
            if self.config_entry is None:
                _LOGGER.warning("No config entry available for token saving")
                return False
                
            # Update the config entry with new tokens
            data = dict(self.config_entry.data)
            data["tokens"] = self._tokens
            
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=data
            )
            _LOGGER.info("Tokens saved successfully")
            return True
        except Exception as e:
            _LOGGER.error("Failed to save tokens: %s", e)
            return False

    def _validate_tokens(self) -> bool:
        """Validate that tokens exist and are not expired."""
        required_keys = [CONF_ACCESS_TOKEN, CONF_REFRESH_TOKEN, CONF_TOKEN_EXPIRES_AT]
        
        if not all(key in self._tokens for key in required_keys):
            return False

        expires_at = self._tokens.get(CONF_TOKEN_EXPIRES_AT)
        if not expires_at:
            return False

        # Check if token expires within the next 5 minutes
        expiry_time = datetime.fromisoformat(expires_at)
        if datetime.now() + timedelta(minutes=5) >= expiry_time:
            return False

        return True

    def get_authorization_url(self) -> str:
        """Get the authorization URL for OAuth2 flow."""
        if not self.client_id:
            raise ValueError("Client ID not set")
        
        _LOGGER.info("Creating authorization URL with client_id: %s", self.client_id)
        
        # Create a new session with the correct client_id for authorization
        auth_session = OAuth2Session(
            self.client_id,
            redirect_uri="https://home-assistant.io/auth/callback",
            scope=OAUTH2_SCOPE,
        )
        
        # Allow HTTP for development (disable SSL verification warnings)
        import os
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        
        auth_url = auth_session.authorization_url(OAUTH2_AUTHORIZE_URL)[0]
        _LOGGER.info("Generated authorization URL: %s", auth_url)
        return auth_url

    def fetch_token(self, authorization_response: str) -> bool:
        """Fetch tokens using authorization response."""
        try:
            # Allow HTTP for development (disable SSL verification warnings)
            import os
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
            
            token = self.session.fetch_token(
                OAUTH2_TOKEN_URL,
                authorization_response=authorization_response,
                client_secret=self.client_secret,
            )
            
            self._tokens = {
                CONF_ACCESS_TOKEN: token["access_token"],
                CONF_REFRESH_TOKEN: token["refresh_token"],
                CONF_TOKEN_EXPIRES_AT: (
                    datetime.now() + timedelta(seconds=token["expires_in"])
                ).isoformat(),
            }
            
            return self.save_tokens()

        except Exception as e:
            _LOGGER.error("Failed to fetch tokens: %s", e)
            return False

    def refresh_tokens(self) -> bool:
        """Refresh the access token using refresh token."""
        try:
            if CONF_REFRESH_TOKEN not in self._tokens:
                _LOGGER.error("No refresh token available")
                return False

            # Allow HTTP for development (disable SSL verification warnings)
            import os
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

            extra = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }

            token = self.session.refresh_token(
                OAUTH2_TOKEN_URL,
                refresh_token=self._tokens[CONF_REFRESH_TOKEN],
                **extra,
            )

            self._tokens = {
                CONF_ACCESS_TOKEN: token["access_token"],
                CONF_REFRESH_TOKEN: token.get("refresh_token", self._tokens[CONF_REFRESH_TOKEN]),
                CONF_TOKEN_EXPIRES_AT: (
                    datetime.now() + timedelta(seconds=token["expires_in"])
                ).isoformat(),
            }

            return self.save_tokens()

        except Exception as e:
            _LOGGER.error("Failed to refresh tokens: %s", e)
            return False

    def get_valid_token(self) -> Optional[str]:
        """Get a valid access token, refreshing if necessary."""
        if not self._tokens:
            if not self.load_tokens():
                return None

        if not self._validate_tokens():
            _LOGGER.info("Token expired, attempting refresh")
            if not self.refresh_tokens():
                return None

        return self._tokens.get(CONF_ACCESS_TOKEN)

    def get_headers(self) -> Dict[str, str]:
        """Get headers with valid access token."""
        token = self.get_valid_token()
        if not token:
            return {}
        
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        } 