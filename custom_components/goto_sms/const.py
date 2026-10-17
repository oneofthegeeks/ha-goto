"""Constants for the GoTo SMS integration."""

DOMAIN = "goto_sms"

# OAuth2 Configuration
OAUTH2_AUTHORIZE_URL = "https://authentication.logmeininc.com/oauth/authorize"
OAUTH2_TOKEN_URL = "https://authentication.logmeininc.com/oauth/token"
OAUTH_SCOPES = ["messaging.v1.send"]

# Service configuration
SERVICE_SEND_SMS = "send_sms"
ATTR_MESSAGE = "message"
ATTR_TARGET = "target"
ATTR_SENDER_ID = "sender_id"
ATTR_TEMPLATE_DATA = "data"
