# Step-by-Step Setup Guide

This guide will walk you through setting up the Home Assistant Wake-Up Automation system from start to finish.

## 📋 Pre-Setup Checklist

Before you begin, ensure you have:

- [ ] Home Assistant running (version 2023.1+)
- [ ] Admin access to Home Assistant
- [ ] Google account with calendar access
- [ ] Smart lights in your son's bedroom
- [ ] Smart TV or streaming device
- [ ] Google Home/Nest speaker
- [ ] Basic understanding of YAML configuration

## 🔧 Step 1: Google Calendar API Setup

### 1.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name your project (e.g., "Home Assistant Calendar")
4. Click "Create"

### 1.2 Enable Google Calendar API

1. In the Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Google Calendar API"
3. Click on it and press "Enable"

### 1.3 Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client ID"
3. Choose "Web application"
4. Add authorized redirect URIs:
   - `http://YOUR_HA_IP:8123/auth/authorize`
   - `https://YOUR_HA_DOMAIN:8123/auth/authorize`
5. Click "Create"
6. Download the JSON file and note the `client_id` and `client_secret`

## 🏠 Step 2: Home Assistant Configuration

### 2.1 Create Secrets File

1. In Home Assistant, go to the `config` folder
2. Create a file called `secrets.yaml`
3. Add your Google credentials:

```yaml
google_client_id: "your-client-id.apps.googleusercontent.com"
google_client_secret: "your-client-secret"
```

### 2.2 Add Calendar Integration

1. Go to Home Assistant → Settings → Devices & Services
2. Click "Add Integration"
3. Search for "Google Calendar"
4. Follow the OAuth flow to authorize access
5. Select your son's calendar

### 2.3 Discover Device Entities

1. Go to Home Assistant → Settings → Devices & Services
2. Look for your smart devices (lights, TV, speakers)
3. Note down the entity IDs for each device
4. Use the device discovery script to help:

```yaml
# Add this to configuration.yaml temporarily
script:
  discover_devices:
    alias: "Discover Devices"
    sequence:
      - service: system_log.write
        data:
          message: "Lights: {{ states.light | map(attribute='entity_id') | list }}"
          level: info
      - service: system_log.write
        data:
          message: "Media Players: {{ states.media_player | map(attribute='entity_id') | list }}"
          level: info
```

## 📁 Step 3: File Installation

### 3.1 Copy Configuration Files

1. Copy `home_assistant_wake_up_automation.yaml` to your Home Assistant `config` folder
2. Copy `google_calendar_integration.yaml` to your `config` folder
3. Copy `device_configuration.yaml` to your `config` folder

### 3.2 Update Device Configuration

Edit `device_configuration.yaml` and replace the placeholder entity IDs with your actual devices:

```yaml
lights:
  sons_bedroom_main: "light.your_actual_light_entity_id"
  sons_bedroom_lamp: "light.your_actual_lamp_entity_id"
  sons_bedroom_strip: "light.your_actual_strip_entity_id"

media_players:
  sons_tv: "media_player.your_actual_tv_entity_id"
  sons_google_speaker: "media_player.your_actual_speaker_entity_id"
```

### 3.3 Update Main Configuration

Add these lines to your `configuration.yaml`:

```yaml
# Include wake-up automation
automation: !include home_assistant_wake_up_automation.yaml
script: !include home_assistant_wake_up_automation.yaml
scene: !include home_assistant_wake_up_automation.yaml
input_select: !include home_assistant_wake_up_automation.yaml
input_boolean: !include home_assistant_wake_up_automation.yaml
input_button: !include home_assistant_wake_up_automation.yaml
template: !include home_assistant_wake_up_automation.yaml

# Include Google Calendar integration
calendar: !include google_calendar_integration.yaml
```

## 🎯 Step 4: Calendar Event Setup

### 4.1 Create Wake-Up Events

In your son's Google Calendar, create these events:

**School Days (Monday-Friday):**
- Title: "Wake Up - School Day"
- Time: 7:00 AM - 7:30 AM
- Recurrence: Daily (Monday-Friday)

**Weekends (Saturday-Sunday):**
- Title: "Wake Up - Weekend"
- Time: 8:00 AM - 8:30 AM
- Recurrence: Weekly (Saturday-Sunday)

**Special Days:**
- Title: "Wake Up - Special Day"
- Time: Custom time
- Recurrence: None (one-time events)

### 4.2 Verify Calendar Integration

1. Go to Home Assistant → Settings → Devices & Services
2. Find your Google Calendar integration
3. Check that events are showing up
4. Look for the "Son's Wake Up Schedule" entity

## 🧪 Step 5: Testing

### 5.1 Test Individual Components

1. **Test Lights:**
   - Go to Home Assistant → Developer Tools → Services
   - Call `light.turn_on` with your light entity IDs
   - Verify lights respond correctly

2. **Test TV:**
   - Call `media_player.turn_on` with your TV entity ID
   - Verify TV turns on and responds

3. **Test Speaker:**
   - Call `media_player.volume_set` with your speaker entity ID
   - Call `media_player.play_media` to test audio playback

### 5.2 Test Complete Automation

1. Go to Home Assistant → Developer Tools → Services
2. Call `input_button.press` with entity `input_button.test_wake_up`
3. Watch the logbook for automation activity
4. Verify all components activate in sequence

### 5.3 Test Calendar Trigger

1. Create a test calendar event for 1 minute in the future
2. Wait for the event to trigger
3. Verify the automation runs automatically

## ⚙️ Step 6: Customization

### 6.1 Adjust Settings

Use the input selectors in Home Assistant to customize:

- **Wake Up Volume**: Choose from Low to Very High
- **Sunrise Duration**: Choose from Quick to Very Slow
- **Wake Up Sound**: Choose from Nature Sounds to Custom Playlist

### 6.2 Toggle Components

Use the input booleans to enable/disable:

- Entire automation
- TV wake-up
- Light wake-up
- Speaker wake-up

### 6.3 Add Custom Media

Edit the media sources in the configuration:

```yaml
# Add your own playlists, URLs, or TTS messages
media_sources:
  custom_playlists:
    - "spotify:playlist:YOUR_PLAYLIST_ID"
    - "https://your-custom-audio-url.com"
```

## 🔍 Step 7: Monitoring and Maintenance

### 7.1 Check Logs

Regularly check Home Assistant logs for any errors:

1. Go to Home Assistant → Settings → System → Logs
2. Look for any automation or device errors
3. Check the logbook for automation activity

### 7.2 Monitor Device States

Keep an eye on device connectivity:

1. Go to Home Assistant → Settings → Devices & Services
2. Check that all devices show as "Available"
3. Restart devices if they show as "Unavailable"

### 7.3 Update Calendar Events

As your son's schedule changes:

1. Update the calendar events in Google Calendar
2. The automation will automatically pick up the changes
3. No Home Assistant configuration changes needed

## 🚨 Troubleshooting Common Issues

### Issue: Calendar Not Updating
**Solution:**
1. Check Google Calendar API credentials
2. Re-authorize the integration
3. Restart Home Assistant

### Issue: Devices Not Responding
**Solution:**
1. Verify entity IDs in configuration
2. Check device connectivity
3. Restart Home Assistant

### Issue: Automation Not Triggering
**Solution:**
1. Check if automation is enabled
2. Verify calendar events exist
3. Test with manual trigger

### Issue: Media Not Playing
**Solution:**
1. Check media URLs/playlists
2. Verify speaker connectivity
3. Test media playback manually

## ✅ Final Checklist

Before considering the setup complete:

- [ ] Google Calendar API configured and working
- [ ] All device entity IDs updated in configuration
- [ ] Calendar events created and visible in Home Assistant
- [ ] All components tested individually
- [ ] Complete automation tested manually
- [ ] Calendar trigger tested with real event
- [ ] Settings customized to preferences
- [ ] Monitoring and maintenance plan in place

## 🎉 You're Done!

Your Home Assistant Wake-Up Automation system is now ready to use! The system will automatically wake up your son based on his Google Calendar schedule, creating a gentle sunrise-like experience with lights, TV, and audio.

Remember to:
- Monitor the system regularly
- Update calendar events as needed
- Customize settings based on your son's preferences
- Keep the system updated and maintained

**Happy Automating! 🌅**