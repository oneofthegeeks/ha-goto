# Home Assistant Wake-Up Automation System

A comprehensive automation system that creates a sunrise-like wake-up experience for your son based on Google Calendar events. This system gradually increases bedroom lights, turns on the TV, and plays wake-up audio through Google speakers.

## 🌅 Features

- **Google Calendar Integration**: Automatically triggers based on calendar events
- **Sunrise Light Simulation**: Gradual light increase over customizable duration
- **TV Wake-Up**: Automatically turns on TV and plays gentle morning content
- **Audio Wake-Up**: Plays nature sounds, music, or TTS messages through Google speakers
- **Customizable Settings**: Adjustable volume, duration, and sound options
- **Manual Testing**: Built-in test buttons for troubleshooting
- **Scene Management**: Pre-configured sleep and wake-up scenes

## 📋 Prerequisites

- Home Assistant (version 2023.1 or later)
- Google Calendar with wake-up events
- Smart lights in your son's bedroom
- Smart TV or streaming device
- Google Home/Nest speaker
- Basic understanding of Home Assistant configuration

## 🚀 Quick Setup

### 1. Install Required Integrations

First, ensure you have these integrations installed in Home Assistant:

- **Google Calendar** (built-in)
- **Google Cast** (for speakers)
- **Media Player** (for TV)
- **Light** (for bedroom lights)

### 2. Configure Google Calendar

1. Go to Google Cloud Console (https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `http://your-home-assistant-ip:8123/auth/authorize`
   - `https://your-home-assistant-domain:8123/auth/authorize`
6. Download credentials and extract `client_id` and `client_secret`

### 3. Set Up Secrets

Copy `secrets_template.yaml` to `secrets.yaml` and fill in your credentials:

```yaml
google_client_id: "your-google-client-id.apps.googleusercontent.com"
google_client_secret: "your-google-client-secret"
```

### 4. Configure Devices

Update `device_configuration.yaml` with your actual device entity IDs:

```yaml
lights:
  sons_bedroom_main: "light.sons_bedroom_main_light"
  sons_bedroom_lamp: "light.sons_bedroom_lamp"
  sons_bedroom_strip: "light.sons_bedroom_led_strip"

media_players:
  sons_tv: "media_player.sons_bedroom_tv"
  sons_google_speaker: "media_player.sons_bedroom_speaker"
```

### 5. Add Configuration to Home Assistant

Add this to your `configuration.yaml`:

```yaml
# Include wake-up automation
automation: !include wake_up_automation.yaml
script: !include wake_up_automation.yaml
scene: !include wake_up_automation.yaml
input_select: !include wake_up_automation.yaml
input_boolean: !include wake_up_automation.yaml
input_button: !include wake_up_automation.yaml
template: !include wake_up_automation.yaml

# Include Google Calendar integration
calendar: !include google_calendar_integration.yaml
```

### 6. Restart Home Assistant

After adding the configuration, restart Home Assistant to load the new automations.

## 📅 Setting Up Calendar Events

Create calendar events in your son's Google Calendar with these naming conventions:

- **"Wake Up - School Day"** (7:00 AM, Monday-Friday)
- **"Wake Up - Weekend"** (8:00 AM, Saturday-Sunday)
- **"Wake Up - Special Day"** (custom time, one-time events)

The automation will trigger automatically when these events start.

## 🎛️ Customization Options

### Wake-Up Volume
- Low (20%)
- Medium (40%) - Default
- High (60%)
- Very High (80%)

### Sunrise Duration
- Quick (5 minutes)
- Normal (10 minutes) - Default
- Slow (15 minutes)
- Very Slow (20 minutes)

### Wake-Up Sound
- Nature Sounds
- Gentle Music
- Alarm Clock (TTS)
- Custom Playlist

### Toggle Options
- Enable/disable entire automation
- Enable/disable TV wake-up
- Enable/disable light wake-up
- Enable/disable speaker wake-up

## 🧪 Testing

Use the built-in test button to verify your setup:

1. Go to Home Assistant → Developer Tools → Services
2. Call `input_button.press` with entity `input_button.test_wake_up`
3. Or use the "Test Wake Up Sequence" button in the UI

## 📱 Usage

### Daily Operation
The automation runs automatically based on your calendar events. No manual intervention required.

### Manual Control
- Use the input selectors in Home Assistant to adjust settings
- Toggle individual components on/off as needed
- Use scenes for quick room state changes

### Monitoring
- Check the logbook for automation activity
- Monitor device states in Home Assistant
- Use the "Next Wake Up Time" sensor to see upcoming events

## 🔧 Troubleshooting

### Calendar Not Updating
1. Check Google Calendar API credentials in `secrets.yaml`
2. Verify calendar permissions in Google Cloud Console
3. Check Home Assistant logs for authentication errors
4. Restart Home Assistant after credential changes

### Devices Not Responding
1. Verify entity IDs in `device_configuration.yaml`
2. Check device connectivity in Home Assistant
3. Use the device discovery script to find correct entity IDs
4. Restart Home Assistant if needed

### Automation Not Triggering
1. Check if automation is enabled in input_boolean
2. Verify calendar events are properly configured
3. Check Home Assistant logs for automation errors
4. Test with manual trigger button

### Media Not Playing
1. Check media player entity IDs
2. Verify media URLs/playlists are accessible
3. Check speaker connectivity
4. Test media playback manually in Home Assistant

## 📁 File Structure

```
/workspace/
├── home_assistant_wake_up_automation.yaml    # Main automation configuration
├── google_calendar_integration.yaml          # Calendar integration setup
├── device_configuration.yaml                 # Device entity configuration
├── wake_up_media_scripts.py                  # Media management helper
├── secrets_template.yaml                     # Template for secrets
├── configuration_include.yaml                # Configuration include file
└── README.md                                 # This documentation
```

## 🔒 Security Notes

- Never commit `secrets.yaml` to version control
- Keep API keys secure and rotate regularly
- Use environment variables in production
- Consider using Home Assistant's built-in secret management

## 🤝 Contributing

Feel free to customize and extend this automation system:

- Add more device types
- Implement weather-based adjustments
- Add more media sources
- Create additional wake-up scenarios

## 📞 Support

For issues and questions:
1. Check Home Assistant logs
2. Verify device connectivity
3. Test individual components
4. Review configuration syntax

## 🎯 Future Enhancements

Potential improvements for the system:

- **Weather Integration**: Adjust wake-up time based on weather
- **Sleep Tracking**: Integrate with sleep monitoring devices
- **Voice Commands**: Add voice control for manual triggers
- **Mobile App**: Create custom mobile interface
- **Analytics**: Track wake-up effectiveness and patterns
- **Multi-Room**: Extend to multiple children's rooms
- **Seasonal Adjustments**: Automatic time changes for daylight saving
- **Holiday Mode**: Special wake-up routines for holidays

## 📄 License

This project is open source and available under the MIT License.

---

**Happy Automating! 🌅**