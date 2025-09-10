# Troubleshooting Guide

This guide helps you diagnose and fix common issues with the Home Assistant Wake-Up Automation system.

## 🔍 General Troubleshooting Steps

### 1. Check Home Assistant Logs

Always start by checking the logs:

1. Go to **Settings** → **System** → **Logs**
2. Look for errors related to:
   - Calendar integration
   - Device connectivity
   - Automation execution
   - Media playback

### 2. Verify Configuration

Check your configuration files for syntax errors:

1. Go to **Settings** → **Server Controls** → **Check Configuration**
2. Fix any syntax errors before restarting
3. Restart Home Assistant after making changes

### 3. Test Individual Components

Before testing the full automation, verify each component works:

1. **Lights**: Test turning on/off manually
2. **TV**: Test power and media playback
3. **Speaker**: Test volume and audio playback
4. **Calendar**: Check if events are visible

## 📅 Calendar Integration Issues

### Problem: Calendar Not Updating

**Symptoms:**
- Calendar events not showing in Home Assistant
- "No upcoming events" in sensor
- Automation not triggering

**Solutions:**

1. **Check API Credentials:**
   ```yaml
   # In secrets.yaml
   google_client_id: "your-client-id.apps.googleusercontent.com"
   google_client_secret: "your-client-secret"
   ```

2. **Re-authorize Integration:**
   - Go to **Settings** → **Devices & Services**
   - Find Google Calendar integration
   - Click "Configure" → "Re-authorize"

3. **Verify Calendar Permissions:**
   - Check Google Cloud Console
   - Ensure Calendar API is enabled
   - Verify OAuth redirect URIs are correct

4. **Check Calendar ID:**
   ```yaml
   # In google_calendar_integration.yaml
   cal_id: "your-sons-calendar@gmail.com"  # Must be exact email
   ```

### Problem: Wrong Calendar Events Triggering

**Symptoms:**
- Automation triggers on wrong events
- Multiple events causing conflicts

**Solutions:**

1. **Filter Events by Title:**
   ```yaml
   # Add condition to automation
   condition:
     - condition: template
       value_template: >
         {{ 'wake up' in trigger.calendar_event.summary | lower }}
   ```

2. **Use Specific Calendar:**
   - Create a dedicated calendar for wake-up events
   - Only include that calendar in the integration

3. **Check Event Times:**
   - Ensure events have correct start/end times
   - Avoid overlapping events

## 💡 Light Control Issues

### Problem: Lights Not Turning On

**Symptoms:**
- Lights remain off during automation
- Error messages in logs
- Entity shows as "Unavailable"

**Solutions:**

1. **Check Entity IDs:**
   ```yaml
   # Verify these match your actual entities
   light.sons_bedroom_main: "light.your_actual_entity_id"
   ```

2. **Test Light Control:**
   - Go to **Developer Tools** → **Services**
   - Call `light.turn_on` with your entity ID
   - Check if light responds

3. **Check Light Integration:**
   - Go to **Settings** → **Devices & Services**
   - Verify light integration is working
   - Check device connectivity

4. **Restart Light Integration:**
   - Disable and re-enable the light integration
   - Restart Home Assistant if needed

### Problem: Lights Not Dimming Gradually

**Symptoms:**
- Lights turn on at full brightness
- No gradual increase effect
- Automation completes too quickly

**Solutions:**

1. **Check Brightness Control:**
   ```yaml
   # Ensure lights support brightness
   - service: light.turn_on
     data:
       brightness: 1  # Start at minimum
   ```

2. **Adjust Duration:**
   - Change sunrise duration setting
   - Increase number of steps in sequence

3. **Check Light Capabilities:**
   - Verify lights support dimming
   - Check if color temperature is supported

## 📺 TV Control Issues

### Problem: TV Not Turning On

**Symptoms:**
- TV remains off during automation
- "Unavailable" status in Home Assistant
- No response to commands

**Solutions:**

1. **Check TV Integration:**
   - Verify TV is connected to network
   - Check if TV integration is working
   - Restart TV if needed

2. **Test TV Control:**
   ```yaml
   # Test basic TV control
   - service: media_player.turn_on
     target:
       entity_id: media_player.sons_tv
   ```

3. **Check TV Entity ID:**
   - Verify correct entity ID in configuration
   - Use device discovery script to find correct ID

4. **TV-Specific Issues:**
   - **Samsung TV**: Check if TV is in developer mode
   - **LG TV**: Verify WebOS integration
   - **Chromecast**: Check if device is on same network

### Problem: TV Not Playing Content

**Symptoms:**
- TV turns on but no content plays
- Error messages about media playback
- Wrong app or channel opens

**Solutions:**

1. **Check Media URLs:**
   ```yaml
   # Verify URLs are accessible
   media_content_id: "https://www.youtube.com/watch?v=VALID_VIDEO_ID"
   ```

2. **Test Media Playback:**
   - Try playing content manually
   - Check if TV supports the media type

3. **Check TV Apps:**
   - Ensure required apps are installed
   - Verify app permissions

## 🔊 Speaker/Audio Issues

### Problem: Speaker Not Playing Audio

**Symptoms:**
- No audio during automation
- Speaker shows as "Unavailable"
- Error messages about media playback

**Solutions:**

1. **Check Speaker Connectivity:**
   - Verify speaker is on same network
   - Check if speaker is responding to commands
   - Restart speaker if needed

2. **Test Audio Playback:**
   ```yaml
   # Test basic audio playback
   - service: media_player.play_media
     target:
       entity_id: media_player.sons_google_speaker
     data:
       media_content_id: "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav"
       media_content_type: "music"
   ```

3. **Check Volume Settings:**
   - Verify volume is not muted
   - Check if volume control is working

4. **Check Media Sources:**
   - Verify audio URLs are accessible
   - Test different media types

### Problem: TTS Not Working

**Symptoms:**
- No speech during automation
- Error messages about TTS service
- Speaker not responding to TTS

**Solutions:**

1. **Check TTS Service:**
   ```yaml
   # Verify TTS service is available
   - service: tts.google_translate_say
     target:
       entity_id: media_player.sons_google_speaker
     data:
       message: "Test message"
       language: "en"
   ```

2. **Install TTS Integration:**
   - Go to **Settings** → **Devices & Services**
   - Add Google Translate TTS integration

3. **Check TTS Configuration:**
   - Verify TTS service is configured
   - Check if language is supported

## 🤖 Automation Issues

### Problem: Automation Not Triggering

**Symptoms:**
- No automation activity in logbook
- Calendar events exist but automation doesn't run
- Manual trigger works but calendar trigger doesn't

**Solutions:**

1. **Check Automation Status:**
   - Go to **Settings** → **Automations & Scenes**
   - Verify automation is enabled
   - Check if conditions are met

2. **Check Calendar Trigger:**
   ```yaml
   # Verify calendar trigger configuration
   trigger:
     - platform: calendar
       entity_id: calendar.sons_wake_up_schedule
       event: start
   ```

3. **Test Manual Trigger:**
   - Use the test button to verify automation works
   - Check if all components respond

4. **Check Automation Conditions:**
   - Verify input_boolean is enabled
   - Check if all required conditions are met

### Problem: Automation Runs But Components Don't Work

**Symptoms:**
- Automation shows as "Running" in logbook
- Some components work, others don't
- Partial automation execution

**Solutions:**

1. **Check Individual Scripts:**
   - Test each script separately
   - Identify which component is failing

2. **Check Script Dependencies:**
   - Verify all required entities exist
   - Check if scripts are properly configured

3. **Check Error Handling:**
   - Look for error messages in logs
   - Add error handling to scripts

## 🔧 Device Discovery Issues

### Problem: Can't Find Device Entity IDs

**Symptoms:**
- Don't know correct entity IDs
- Devices not showing in Home Assistant
- Configuration errors due to wrong IDs

**Solutions:**

1. **Use Device Discovery Script:**
   ```yaml
   # Add this to configuration.yaml
   script:
     discover_devices:
       alias: "Discover Devices"
       sequence:
         - service: system_log.write
           data:
             message: "Lights: {{ states.light | map(attribute='entity_id') | list }}"
             level: info
   ```

2. **Check Devices & Services:**
   - Go to **Settings** → **Devices & Services**
   - Look for your device integrations
   - Note down entity IDs

3. **Use Entity Registry:**
   - Go to **Settings** → **Devices & Services** → **Entities**
   - Search for your devices
   - Copy the exact entity IDs

## 📱 Network and Connectivity Issues

### Problem: Devices Not Responding

**Symptoms:**
- Devices show as "Unavailable"
- Intermittent connectivity issues
- Automation fails randomly

**Solutions:**

1. **Check Network Connectivity:**
   - Verify devices are on same network
   - Check WiFi signal strength
   - Restart router if needed

2. **Check Device Status:**
   - Verify devices are powered on
   - Check if devices are responding to other commands

3. **Restart Devices:**
   - Power cycle problematic devices
   - Restart Home Assistant
   - Check if issues persist

## 🚨 Emergency Troubleshooting

### If Nothing Works

1. **Disable Automation:**
   - Turn off `input_boolean.enable_wake_up_automation`
   - This prevents automation from running

2. **Check Basic Functionality:**
   - Test each device individually
   - Verify Home Assistant is working
   - Check network connectivity

3. **Restart Everything:**
   - Restart Home Assistant
   - Restart all smart devices
   - Check if issues persist

4. **Check Configuration:**
   - Verify all configuration files are correct
   - Check for syntax errors
   - Restore from backup if needed

### Getting Help

If you're still having issues:

1. **Check Home Assistant Forums:**
   - Search for similar issues
   - Post your specific problem

2. **Check Integration Documentation:**
   - Read the official documentation
   - Look for known issues

3. **Enable Debug Logging:**
   ```yaml
   # Add to configuration.yaml
   logger:
     default: info
     logs:
       homeassistant.components.calendar: debug
       homeassistant.components.light: debug
       homeassistant.components.media_player: debug
   ```

4. **Create Minimal Test Case:**
   - Create a simple automation with just one component
   - Test if basic functionality works
   - Gradually add complexity

## 📋 Maintenance Checklist

Regular maintenance to prevent issues:

- [ ] Check device connectivity weekly
- [ ] Verify calendar events monthly
- [ ] Update Home Assistant regularly
- [ ] Monitor logs for errors
- [ ] Test automation monthly
- [ ] Update device firmware
- [ ] Check network stability
- [ ] Backup configuration regularly

Remember: Most issues are caused by simple configuration errors or device connectivity problems. Start with the basics and work your way up to more complex troubleshooting.