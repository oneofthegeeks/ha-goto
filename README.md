# GoTo SMS Integration for Home Assistant

[![Test Integration](https://github.com/your-username/ha-goto/workflows/Test%20Integration/badge.svg)](https://github.com/your-username/ha-goto/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A custom Home Assistant integration that allows you to send SMS messages using the GoTo Connect API.

## Features

- **OAuth2 Authentication**: Secure authentication using GoTo Connect's OAuth2 flow
- **Automatic Token Refresh**: Automatically refreshes expired access tokens
- **SMS Notifications**: Send SMS messages via the `notify.goto_sms` service
- **Error Handling**: Comprehensive error logging and handling
- **Async Compatible**: Built with async/await patterns for better performance

## Installation

### Method 1: Manual Installation

1. Copy the `custom_components/goto_sms` folder to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. The integration will be available in the Integrations page

### Method 2: Using Git

```bash
cd /path/to/homeassistant/config/custom_components
git clone https://github.com/your-username/ha-goto.git
cp -r ha-goto/custom_components/goto_sms ./
rm -rf ha-goto
```

Then restart Home Assistant.

## Configuration

### Prerequisites

1. **GoTo Connect Account**: You need a GoTo Connect account with SMS capabilities
2. **OAuth2 Application**: Create an OAuth2 application in your GoTo Connect developer portal
3. **API Credentials**: Obtain your Client ID and Client Secret from GoTo Connect

### Setup Steps

1. **Create OAuth2 Application**:
   - Log into your GoTo Connect developer portal
   - Create a new OAuth2 application
   - Set the redirect URI to `https://home-assistant.io/auth/callback`
   - Note your Client ID and Client Secret

2. **Configure Integration**:
   - In Home Assistant, go to **Settings** → **Devices & Services**
   - Click **Add Integration**
   - Search for "GoTo SMS" and select it
   - Enter your Client ID and Client Secret in the configuration form
   - Complete the OAuth2 authorization flow by visiting the provided URL
   - Paste the authorization response back into the form

3. **Test the Integration**:
   - Use the Developer Tools → Services
   - Call the `notify.goto_sms` service with:
     ```yaml
     message: "Hello from Home Assistant!"
     target: "+1234567890"
     sender_id: "MyHome"  # Optional
     ```

## Usage

### Service Call

Send an SMS using the notification service:

```yaml
service: notify.goto_sms
data:
  message: "Your garage door is open!"
  target: "+1234567890"
  sender_id: "HomeAssistant"  # Optional
```

### Automation Example

```yaml
automation:
  - alias: "Send SMS when motion detected"
    trigger:
      platform: state
      entity_id: binary_sensor.motion_sensor
      to: "on"
    action:
      - service: notify.goto_sms
        data:
          message: "Motion detected in your home!"
          target: "+1234567890"
```

### Script Example

```yaml
script:
  send_test_sms:
    alias: "Send Test SMS"
    sequence:
      - service: notify.goto_sms
        data:
          message: "This is a test message from Home Assistant"
          target: "+1234567890"
          sender_id: "TestSystem"
```

## Configuration Options

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `client_id` | string | Yes | Your GoTo Connect OAuth2 Client ID |
| `client_secret` | string | Yes | Your GoTo Connect OAuth2 Client Secret |

## Service Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message` | string | Yes | The SMS message to send |
| `target` | string | Yes | Phone number with country code (e.g., "+1234567890") |
| `sender_id` | string | No | Sender ID for the SMS (defaults to "HomeAssistant") |

## Token Storage

The integration stores OAuth2 tokens securely within the Home Assistant config entry system. The tokens are automatically refreshed when they expire and are managed by the integration.

## Troubleshooting

### Common Issues

1. **Authentication Failed**:
   - Check your Client ID and Client Secret
   - Ensure your OAuth2 application is properly configured
   - Verify the redirect URI matches exactly

2. **SMS Not Sending**:
   - Check the target phone number format (include country code)
   - Verify your GoTo Connect account has SMS capabilities
   - Check the Home Assistant logs for detailed error messages

3. **Token Refresh Issues**:
   - Delete the token file and re-authenticate
   - Check your internet connection
   - Verify the GoTo Connect API endpoints are accessible

### Logs

Enable debug logging by adding to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.goto_sms: debug
```

## Development

### File Structure

```
custom_components/goto_sms/
├── __init__.py          # Integration initialization
├── manifest.json        # Integration metadata
├── const.py            # Constants and configuration
├── oauth.py            # OAuth2 token management
├── notify.py           # SMS notification service
└── services.yaml       # Service definitions
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- [Create an issue](https://github.com/your-username/ha-goto/issues) on GitHub
- Check the [Home Assistant community forums](https://community.home-assistant.io/)
- Review the logs for detailed error information

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 