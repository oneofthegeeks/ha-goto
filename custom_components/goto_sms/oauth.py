"""OAuth2 token management for GoTo SMS integration."""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

import requests
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
from requests_oauthlib import OAuth2Session

# Allow HTTP for development (disable SSL verification warnings)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

from .const import (
    CONF_ACCESS_TOKEN,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_REFRESH_TOKEN,
    CONF_TOKEN_EXPIRES_AT,
    DOMAIN,
    OAUTH2_AUTHORIZE_URL,
    OAUTH2_SCOPE,
    OAUTH2_TOKEN_URL,
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
            _LOGGER.debug("load_tokens() called")
            if self.config_entry is None:
                _LOGGER.warning("No config entry available for token loading")
                return False

            _LOGGER.info(
                "Loading tokens from config entry. Config entry data: %s",
                self.config_entry.data,
            )

            tokens = self.config_entry.data.get("tokens", {})
            _LOGGER.info("Found tokens in config entry: %s", tokens)

            if not tokens:
                _LOGGER.warning("No tokens found in config entry")
                _LOGGER.warning("This may indicate the integration needs to be re-authenticated")
                return False

            self._tokens = tokens
            _LOGGER.info("Tokens loaded into memory: %s", self._tokens)

            if not self._validate_tokens():
                _LOGGER.warning("Invalid or expired tokens found")
                _LOGGER.warning("Attempting to refresh tokens...")
                if not self.refresh_tokens():
                    _LOGGER.error("Failed to refresh tokens. Re-authentication required.")
                    return False
                return True

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

            # Schedule the update in the main event loop (non-blocking)
            self.hass.async_create_task(self._update_config_entry_async(data))
            _LOGGER.info("Tokens scheduled for saving")
            return True
        except Exception as e:
            _LOGGER.error("Failed to schedule token saving: %s", e)
            return False

    async def _update_config_entry_async(self, data):
        """Update config entry asynchronously."""
        try:
            self.hass.config_entries.async_update_entry(self.config_entry, data=data)
        except Exception as e:
            _LOGGER.error("Failed to update config entry: %s", e)

    def _validate_tokens(self) -> bool:
        """Validate that tokens exist and are not expired."""
        required_keys = [CONF_ACCESS_TOKEN, CONF_REFRESH_TOKEN, CONF_TOKEN_EXPIRES_AT]

        _LOGGER.info("Validating tokens. Available keys: %s", list(self._tokens.keys()))

        if not all(key in self._tokens for key in required_keys):
            missing_keys = [key for key in required_keys if key not in self._tokens]
            _LOGGER.info("Missing required token keys: %s", missing_keys)
            return False

        expires_at = self._tokens.get(CONF_TOKEN_EXPIRES_AT)
        if not expires_at:
            _LOGGER.info("No expiration time found")
            return False

        # Check if token expires within the next 5 minutes
        try:
            expiry_time = datetime.fromisoformat(expires_at)
            current_time = datetime.now()
            time_until_expiry = expiry_time - current_time

            _LOGGER.info(
                "Token validation - expires_at: %s, current_time: %s, time_until_expiry: %s",
                expires_at,
                current_time,
                time_until_expiry,
            )

            # Token is valid if it expires more than 5 minutes from now
            if time_until_expiry <= timedelta(minutes=5):
                _LOGGER.info("Token expires within 5 minutes - will refresh")
                return False

            _LOGGER.info("Token is valid")
            return True
        except Exception as e:
            _LOGGER.error("Error parsing token expiration time: %s", e)
            return False

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

        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        auth_url = auth_session.authorization_url(OAUTH2_AUTHORIZE_URL)[0]
        _LOGGER.info("Generated authorization URL: %s", auth_url)
        return auth_url

    def fetch_token(self, authorization_response: str) -> bool:
        """Fetch tokens using authorization response."""
        try:
            import base64
            import re
            import urllib.parse

            # Try different ways to extract the authorization code
            code = None

            # Method 1: Try to parse as URL with query parameters
            if authorization_response.startswith("http"):
                try:
                    parsed_url = urllib.parse.urlparse(authorization_response)
                    query_params = urllib.parse.parse_qs(parsed_url.query)
                    code = query_params.get("code", [None])[0]
                    _LOGGER.debug(
                        "Extracted code from URL: %s",
                        code[:10] + "..." if code else "None",
                    )
                except Exception as e:
                    _LOGGER.debug("Failed to parse as URL: %s", e)

            # Method 2: Try to extract code from the response string directly
            if not code:
                code_match = re.search(r"[?&]code=([^&]+)", authorization_response)
                if code_match:
                    code = code_match.group(1)
                    _LOGGER.debug(
                        "Extracted code using regex: %s",
                        code[:10] + "..." if code else "None",
                    )

            # Method 3: If the response looks like just a code
            if (
                not code
                and len(authorization_response.strip()) < 100
                and "=" not in authorization_response
            ):
                code = authorization_response.strip()
                _LOGGER.debug(
                    "Using response as code directly: %s",
                    code[:10] + "..." if code else "None",
                )

            if not code:
                _LOGGER.error(
                    "No authorization code found in response: %s",
                    (
                        authorization_response[:100] + "..."
                        if len(authorization_response) > 100
                        else authorization_response
                    ),
                )
                return False

            # Create Basic auth header with client credentials
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()

            # Prepare the request data
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": "https://home-assistant.io/auth/callback",
            }

            # Make the token request
            response = requests.post(
                OAUTH2_TOKEN_URL,
                headers={
                    "Authorization": f"Basic {encoded_credentials}",
                    "Accept": "application/json",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data=data,
                timeout=30,
            )

            if response.status_code != 200:
                _LOGGER.error(
                    "Token request failed: %d - %s", response.status_code, response.text
                )
                return False

            token_data = response.json()

            self._tokens = {
                CONF_ACCESS_TOKEN: token_data["access_token"],
                CONF_REFRESH_TOKEN: token_data["refresh_token"],
                CONF_TOKEN_EXPIRES_AT: (
                    datetime.now() + timedelta(seconds=token_data["expires_in"])
                ).isoformat(),
            }

            # Only try to save tokens if we have a config entry
            if self.config_entry is not None:
                return self.save_tokens()
            else:
                # During setup, just store tokens in memory
                _LOGGER.info("Tokens fetched successfully during setup")
                return True

        except Exception as e:
            _LOGGER.error("Failed to fetch tokens: %s", e)
            return False

    def refresh_tokens(self) -> bool:
        """Refresh the access token using refresh token."""
        try:
            if CONF_REFRESH_TOKEN not in self._tokens:
                _LOGGER.error("No refresh token available")
                return False

            import base64

            # Create Basic auth header with client credentials
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()

            # Prepare the request data
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self._tokens[CONF_REFRESH_TOKEN],
            }

            # Make the token refresh request
            response = requests.post(
                OAUTH2_TOKEN_URL,
                headers={
                    "Authorization": f"Basic {encoded_credentials}",
                    "Accept": "application/json",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data=data,
                timeout=30,
            )

            if response.status_code != 200:
                _LOGGER.error(
                    "Token refresh failed: %d - %s", response.status_code, response.text
                )
                return False

            token_data = response.json()

            self._tokens = {
                CONF_ACCESS_TOKEN: token_data["access_token"],
                CONF_REFRESH_TOKEN: token_data.get(
                    "refresh_token", self._tokens[CONF_REFRESH_TOKEN]
                ),
                CONF_TOKEN_EXPIRES_AT: (
                    datetime.now() + timedelta(seconds=token_data["expires_in"])
                ).isoformat(),
            }

            return self.save_tokens()

        except Exception as e:
            _LOGGER.error("Failed to refresh tokens: %s", e)
            return False

    def get_valid_token(self) -> Optional[str]:
        """Get a valid access token, refreshing if necessary."""
        _LOGGER.debug("get_valid_token() called")
        _LOGGER.info("Getting valid token. Current tokens: %s", self._tokens)

        if not self._tokens:
            _LOGGER.info("No tokens in memory, attempting to load from config entry")
            if not self.load_tokens():
                _LOGGER.error("Failed to load tokens from config entry")
                return None

        if not self._validate_tokens():
            _LOGGER.info("Token expired, attempting refresh")
            if not self.refresh_tokens():
                _LOGGER.error("Failed to refresh tokens")
                return None

        token = self._tokens.get(CONF_ACCESS_TOKEN)
        _LOGGER.info("Returning token: %s", "present" if token else "none")
        return token

    def get_headers(self) -> Dict[str, str]:
        """Get headers with valid access token."""
        _LOGGER.debug("get_headers() called")
        token = self.get_valid_token()
        if not token:
            _LOGGER.error("No valid token available. Tokens: %s", self._tokens)
            _LOGGER.error("Config entry data: %s", self.config_entry.data if self.config_entry else "None")
            
            # Trigger re-authentication if we have a config entry
            if self.config_entry:
                _LOGGER.info("Triggering re-authentication flow")
                self._trigger_reauth()
            
            return {}

        _LOGGER.info("Got valid token, creating headers")
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def _trigger_reauth(self) -> None:
        """Trigger re-authentication flow."""
        try:
            if self.config_entry:
                _LOGGER.info("Triggering re-authentication for config entry: %s", self.config_entry.entry_id)
                
                # Import here to avoid circular imports
                from homeassistant import config_entries
                
                # Trigger the re-authentication flow
                self.hass.async_create_task(
                    self.hass.config_entries.flow.async_init(
                        DOMAIN,
                        context={"source": config_entries.SOURCE_REAUTH},
                        data=self.config_entry.data,
                    )
                )
                _LOGGER.info("Re-authentication flow triggered successfully")
            else:
                _LOGGER.warning("No config entry available for re-authentication")
        except Exception as e:
            _LOGGER.error("Failed to trigger re-authentication: %s", e)
