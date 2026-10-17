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

# Voice (optional SIP options on the config entry)
SERVICE_CALL_TTS = "call_tts"
ATTR_TTS_ENGINE = "tts_engine"
ATTR_LANGUAGE = "language"
ATTR_REPEAT = "repeat"
ATTR_RING_TIMEOUT = "ring_timeout"
CONF_SIP_USERNAME = "sip_username"
CONF_SIP_PASSWORD = "sip_password"
CONF_SIP_SERVER = "sip_server"
CONF_SIP_PROXY = "sip_proxy"
DEFAULT_SIP_SERVER = "reg.jiveip.net"
