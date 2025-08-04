# GoTo SMS Integration for Home Assistant

[![Test Integration](https://github.com/oneofthegeeks/ha-goto/workflows/Test%20Integration/badge.svg)](https://github.com/oneofthegeeks/ha-goto/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/docs/setup/prerequisites)

A custom Home Assistant integration that allows you to send SMS messages using the GoTo Connect API.

## Features

- **OAuth2 Authentication**: Secure authentication using GoTo Connect's OAuth2 flow
- **Automatic Token Refresh**: Automatically refreshes expired access tokens
- **SMS Notifications**: Send SMS messages via the `goto_sms.send_sms` service
- **Template Support**: Dynamic messages using Home Assistant templates
- **Message Tracking**: Automatic tracking of sent SMS messages with dashboard integration
- **Error Handling**: Comprehensive error logging and handling
- **Async Compatible**: Built with async/await patterns for better performance

## SMS Message Tracking

You can manually track SMS messages by incrementing a counter in your automations. Here's how to set it up:

### Simple Input Number Tracking

Add to your `configuration.yaml`:
```yaml
input_number:
  sms_messages_sent:
    name: "SMS Messages Sent"
    min: 0
    max: 999999
    step: 1
    icon: mdi:message-text
    unit_of_measurement: "messages"
```

### Automation Example

```yaml
automation:
  - alias: "Send SMS and track count"
    trigger:
      platform: state
      entity_id: binary_sensor.motion_sensor
      to: "on"
    action:
      # Send the SMS
      - service: goto_sms.send_sms
        data:
          message: "Motion detected!"
          target: "+1234567890"
          sender_id: "+1234567890"
      
      # Increment the counter
      - service: input_number.set_value
        data:
          entity_id: input_number.sms_messages_sent
          value: "{{ states('input_number.sms_messages_sent') | int + 1 }}"
```

### Dashboard Example

```yaml
# Simple statistics card
type: entities
title: "SMS Statistics"
entities:
  - entity: input_number.sms_messages_sent
    name: "Total SMS Sent"
```

## Installation

### Method 1: HACS (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Add this repository as a custom repository in HACS
3. Search for "GoTo SMS" in the HACS store
4. Click "Download" and restart Home Assistant

### Method 2: Manual Installation

1. Download this repository
2. Copy the `custom_components/goto_sms` folder to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant
4. The integration will be available in the Integrations page

### Method 3: Automated Installation

Run the installation script from the repository root:

```bash
./install.sh
```

The script will auto-detect your Home Assistant installation and guide you through the process.

## Updating

### HACS Users (Recommended)

If you installed via HACS, updates are automatic:

1. **Automatic Updates**: HACS will notify you when updates are available
2. **Manual Update**: Go to HACS → Integrations → GoTo SMS → Update
3. **Restart**: After updating, restart Home Assistant

### Manual Installation Updates

#### Option 1: Using the Install Script (Recommended)

```bash
# Navigate to the repository directory
cd /path/to/ha-goto

# Pull latest changes
git pull origin main

# Run the install script (it handles backups automatically)
./install.sh
```

#### Option 2: Manual Update

1. **Backup your current installation**:
   ```bash
   cp -r /config/custom_components/goto_sms /config/custom_components/goto_sms.backup
   ```

2. **Download the latest version**:
   - Download from GitHub releases, or
   - Clone the repository: `git clone https://github.com/oneofthegeeks/ha-goto.git`

3. **Replace the integration**:
   ```bash
   cp -r custom_components/goto_sms /config/custom_components/
   ```

4. **Restart Home Assistant**

#### Option 3: Using the Dedicated Update Script (Recommended)

The repository includes a dedicated update script:

```bash
# Run the update script
./update.sh
```

The script will:
- Automatically detect your Home Assistant installation
- Create a backup of your current installation
- Pull the latest changes from the repository
- Install the updated integration
- Provide clear next steps

#### Option 4: Create Your Own Update Script

Create a reusable update script for easier future updates:

```bash
#!/bin/bash
# update_goto_sms.sh
cd /path/to/ha-goto
git pull origin main
./install.sh
```

Make it executable: `chmod +x update_goto_sms.sh`

### Post-Update Steps

After updating:

1. **Restart Home Assistant** to load the new version
2. **Check the CHANGELOG** for any breaking changes
3. **Test the integration** with a simple SMS
4. **Review your automations** if there were major changes

### Troubleshooting Updates

#### Integration Not Working After Update

1. **Check logs** for errors:
   ```yaml
   logger:
     default: info
     logs:
       custom_components.goto_sms: debug
   ```

2. **Restore from backup** if needed:
   ```bash
   rm -rf /config/custom_components/goto_sms
   cp -r /config/custom_components/goto_sms.backup /config/custom_components/goto_sms
   ```

3. **Re-authenticate** if OAuth tokens are invalid

#### Version Compatibility

- Check the `manifest.json` for minimum Home Assistant version requirements
- Review the CHANGELOG for breaking changes
- Test thoroughly after major version updates

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
   - Call the `goto_sms.send_sms` service with:
     ```yaml
     message: "Hello from Home Assistant!"
     target: "+1234567890"
     sender_id: "+1234567890"  # Your GoTo phone number in E.164 format
     ```

## Usage

### Service Call

Send an SMS using the service:

```yaml
service: goto_sms.send_sms
data:
  message: "Your garage door is open!"
  target: "+1234567890"
  sender_id: "+1234567890"  # Your GoTo phone number in E.164 format
```

### Template Support

The integration supports Home Assistant templates for dynamic messages:

#### Basic Template Example

```yaml
service: goto_sms.send_sms
data:
  message: "Temperature is {{ states('sensor.living_room_temperature') }}°F"
  target: "+1234567890"
  sender_id: "+1234567890"
```

#### Advanced Template with Data

```yaml
service: goto_sms.send_sms
data:
  message: "Alert: {{ data.location }} sensor triggered at {{ now().strftime('%H:%M') }}"
  target: "+1234567890"
  sender_id: "+1234567890"
  data:
    location: "kitchen"
```

#### Template with Entity States

```yaml
service: goto_sms.send_sms
data:
  message: |
    Home Status Update:
    - Temperature: {{ states('sensor.living_room_temperature') }}°F
    - Humidity: {{ states('sensor.living_room_humidity') }}%
    - Motion: {{ states('binary_sensor.motion_sensor') }}
    - Door: {{ states('binary_sensor.front_door') }}
  target: "+1234567890"
  sender_id: "+1234567890"
```

### Automation Examples

#### Send SMS when motion detected with template:

```yaml
automation:
  - alias: "Send SMS when motion detected"
    trigger:
      platform: state
      entity_id: binary_sensor.motion_sensor
      to: "on"
    action:
      - service: goto_sms.send_sms
        data:
          message: "Motion detected at {{ now().strftime('%H:%M on %Y-%m-%d') }}"
          target: "+1234567890"
          sender_id: "+1234567890"
```

#### Send SMS with sensor data:

```yaml
automation:
  - alias: "Temperature alert with template"
    trigger:
      platform: numeric_state
      entity_id: sensor.living_room_temperature
      above: 80
    action:
      - service: goto_sms.send_sms
        data:
          message: |
            Temperature Alert!
            Current: {{ states('sensor.living_room_temperature') }}°F
            Humidity: {{ states('sensor.living_room_humidity') }}%
            Time: {{ now().strftime('%H:%M') }}
          target: "+1234567890"
          sender_id: "+1234567890"
```

#### Send SMS with custom data:

```yaml
automation:
  - alias: "Custom alert with template data"
    trigger:
      platform: state
      entity_id: binary_sensor.front_door
      to: "on"
    action:
      - service: goto_sms.send_sms
        data:
          message: "{{ data.event_type }} detected in {{ data.zone }}"
          target: "+1234567890"
          sender_id: "+1234567890"
          data:
            event_type: "Door opening"
            zone: "front entrance"
```

### Script Example

```yaml
script:
  send_test_sms:
    alias: "Send Test SMS"
    sequence:
      - service: goto_sms.send_sms
        data:
          message: "This is a test message from Home Assistant"
          target: "+1234567890"
          sender_id: "+1234567890"  # Your GoTo phone number in E.164 format
```

## Configuration Options

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `client_id` | string | Yes | Your GoTo Connect OAuth2 Client ID |
| `client_secret` | string | Yes | Your GoTo Connect OAuth2 Client Secret |

## Service Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message` | string | Yes | The SMS message to send (supports templates) |
| `target` | string | Yes | Phone number with country code (e.g., "+1234567890") |
| `sender_id` | string | Yes | GoTo phone number in E.164 format to send from (e.g., "+1234567890") |
| `data` | object | No | Optional data for template rendering |

## Template Features

### Supported Template Functions

- **Entity States**: `{{ states('sensor.temperature') }}`
- **Time Functions**: `{{ now().strftime('%H:%M') }}`
- **Conditional Logic**: `{% if states('binary_sensor.motion') == 'on' %}Motion detected{% else %}No motion{% endif %}`
- **Custom Data**: `{{ data.location }}` (when using the `data` parameter)

### Template Examples

#### Time-based Messages
```yaml
message: "Alert at {{ now().strftime('%H:%M on %Y-%m-%d') }}"
```

#### Sensor Data
```yaml
message: "Temperature: {{ states('sensor.living_room_temperature') }}°F"
```

#### Conditional Messages
```yaml
message: "{% if states('binary_sensor.motion') == 'on' %}Motion detected{% else %}No motion{% endif %}"
```

#### Multi-line Status
```yaml
message: |
  Home Status:
  - Temperature: {{ states('sensor.temperature') }}°F
  - Motion: {{ states('binary_sensor.motion') }}
  - Time: {{ now().strftime('%H:%M') }}
```

## Token Storage

The integration stores OAuth2 tokens securely within the Home Assistant config entry system. The tokens are automatically refreshed when they expire and are managed by the integration.

## Troubleshooting

### Common Issues

1. **Authentication Failed**:
   - Check your Client ID and Client Secret
   - Ensure your OAuth2 application is properly configured
   - Verify the redirect URI matches exactly
   - **Re-authentication**: If tokens expire, the integration will automatically trigger re-authentication

2. **SMS Not Sending**:
   - Check the target phone number format (include country code)
   - Verify your GoTo Connect account has SMS capabilities
   - Check the Home Assistant logs for detailed error messages

3. **Template Rendering Issues**:
   - Check template syntax for errors
   - Verify entity names exist
   - Enable debug logging to see template rendering details

4. **Token Refresh Issues**:
   - The integration will automatically trigger re-authentication when tokens expire
   - Check your internet connection
   - Verify the GoTo Connect API endpoints are accessible

### Re-authentication

The integration now supports automatic re-authentication when tokens expire:

1. **Automatic Detection**: The integration detects when tokens are expired or invalid
2. **UI Re-authentication**: A re-authentication prompt will appear in your Home Assistant UI
3. **Seamless Process**: Follow the OAuth flow again without losing your configuration
4. **Preserved Settings**: Your existing configuration is maintained during re-authentication

**To manually trigger re-authentication:**
1. Go to **Settings** → **Devices & Services**
2. Find your GoTo SMS integration
3. Click the three dots (⋮) and select **Reconfigure**
4. Follow the OAuth flow again

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
├── config_flow.py      # Configuration flow
├── services.yaml       # Service definitions
└── translations/
    └── en/
        └── config_flow.json # UI translations
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
- [Create an issue](https://github.com/oneofthegeeks/ha-goto/issues) on GitHub
- Check the [Home Assistant community forums](https://community.home-assistant.io/)
- Review the logs for detailed error information

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 