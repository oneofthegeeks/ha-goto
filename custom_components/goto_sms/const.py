"""Constants for the GoTo SMS integration."""

DOMAIN = "goto_sms"
DEFAULT_NAME = "GoTo SMS"

# OAuth2 Configuration
OAUTH2_AUTHORIZE_URL = "https://authentication.logmeininc.com/oauth/authorize"
OAUTH2_TOKEN_URL = "https://authentication.logmeininc.com/oauth/token"
OAUTH2_SCOPE = "messaging.v1.send"

# GoTo Connect API Endpoints
GOTO_API_BASE_URL = "https://api.goto.com"
SMS_ENDPOINT = "/messaging/v1/messages"

# Configuration keys
CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"
CONF_ACCESS_TOKEN = "access_token"
CONF_REFRESH_TOKEN = "refresh_token"
CONF_TOKEN_EXPIRES_AT = "token_expires_at"

# Service configuration
SERVICE_SEND_SMS = "send_sms"
ATTR_MESSAGE = "message"
ATTR_TARGET = "target"
ATTR_SENDER_ID = "sender_id"

# Default values
# Note: sender_id is required and must be a valid GoTo phone number in E.164 format 