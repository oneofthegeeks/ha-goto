"""Constants for the GoTo SMS integration."""

DOMAIN = "goto_sms"
DEFAULT_NAME = "GoTo SMS"

# OAuth2 Configuration
OAUTH2_AUTHORIZE_URL = "https://authentication.logmeininc.com/oauth/authorize"
OAUTH2_TOKEN_URL = "https://authentication.logmeininc.com/oauth/token"
OAUTH2_SCOPE = "sms:send"

# GoTo Connect API Endpoints
GOTO_API_BASE_URL = "https://api.goto.com"
SMS_ENDPOINT = "/v1/sms/messages"

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
DEFAULT_SENDER_ID = "HomeAssistant" 