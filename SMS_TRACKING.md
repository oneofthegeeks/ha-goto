# SMS Message Tracking

The GoTo SMS integration now includes automatic message tracking capabilities. This feature allows you to monitor how many SMS messages have been sent through your Home Assistant dashboard.

## 📊 Tracking Options

The integration supports **two tracking methods** - you can use either or both:

### Option 1: Simple Input Number (Recommended for Beginners)

**Setup:**
Add this to your `configuration.yaml`:

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

**Features:**
- ✅ Simple setup
- ✅ Works with Home Assistant's built-in statistics
- ✅ Can be reset manually
- ✅ Compatible with all dashboard cards
- ✅ Automatic tracking (no additional configuration needed)

### Option 2: Advanced Sensor (Recommended for Power Users)

**Setup:**
The sensor is automatically created when you install the integration. No additional configuration needed.

**Features:**
- ✅ Automatic daily/weekly/monthly tracking
- ✅ Persistent storage across restarts
- ✅ Detailed attributes (daily, weekly, monthly, total counts)
- ✅ Automatic reset of daily/weekly/monthly counters
- ✅ Advanced dashboard capabilities

## 📈 Dashboard Examples

### Simple Dashboard Card

```yaml
type: entities
title: "SMS Statistics"
entities:
  - entity: input_number.sms_messages_sent
    name: "Total SMS Sent"
  - entity: sensor.sms_messages_sent
    name: "Advanced SMS Counter"
```

### Statistics Dashboard

```yaml
type: statistics-graph
title: "SMS Messages Over Time"
entities:
  - entity: input_number.sms_messages_sent
    name: "SMS Messages"
stat_types:
  - daily_on_time
  - daily_off_time
  - daily_average
```

### Custom Template Sensors

Create additional sensors for different time periods:

```yaml
template:
  - sensor:
      - name: "SMS Messages Today"
        state: "{{ states('sensor.sms_messages_sent').attributes.daily_count }}"
        attributes:
          friendly_name: "SMS Messages Today"
          icon: mdi:calendar-today
      
      - name: "SMS Messages This Week"
        state: "{{ states('sensor.sms_messages_sent').attributes.weekly_count }}"
        attributes:
          friendly_name: "SMS Messages This Week"
          icon: mdi:calendar-week
      
      - name: "SMS Messages This Month"
        state: "{{ states('sensor.sms_messages_sent').attributes.monthly_count }}"
        attributes:
          friendly_name: "SMS Messages This Month"
          icon: mdi:calendar-month
```

## 🔧 Configuration

### Automatic Tracking

Both tracking methods work automatically - no additional configuration needed. The integration will:

1. **Automatically increment counters** when SMS messages are sent successfully
2. **Handle failed messages** - counters only increment for successful sends
3. **Persist data** across Home Assistant restarts
4. **Reset counters** automatically (daily for sensor, manual for input_number)

### Manual Reset

**Input Number Method:**
```yaml
service: input_number.set_value
target:
  entity_id: input_number.sms_messages_sent
data:
  value: 0
```

**Sensor Method:**
The sensor automatically resets daily/weekly/monthly counters. Total count persists.

## 📊 Available Data

### Input Number Entity
- **State**: Total number of messages sent
- **Unit**: messages
- **Icon**: mdi:message-text

### Sensor Entity
- **State**: Total number of messages sent
- **Attributes**:
  - `daily_count`: Messages sent today
  - `weekly_count`: Messages sent this week
  - `monthly_count`: Messages sent this month
  - `total_count`: Total messages sent
  - `last_reset`: Date of last reset

## 🎯 Use Cases

### 1. Cost Tracking
Monitor your SMS usage to track costs:
```yaml
template:
  - sensor:
      - name: "SMS Cost This Month"
        state: "{{ (states('sensor.sms_messages_sent').attributes.monthly_count | int) * 0.05 }}"
        attributes:
          friendly_name: "SMS Cost This Month"
          unit_of_measurement: "$"
```

### 2. Usage Alerts
Create automations to alert when usage is high:
```yaml
automation:
  - alias: "SMS Usage Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.sms_messages_sent
      above: 100
    action:
      - service: notify.mobile_app
        data:
          message: "High SMS usage detected: {{ states('sensor.sms_messages_sent') }} messages"
```

### 3. Daily Reports
Send daily SMS usage reports:
```yaml
automation:
  - alias: "Daily SMS Report"
    trigger:
      platform: time
      at: "08:00:00"
    action:
      - service: goto_sms.send_sms
        data:
          message: "Daily SMS Report: {{ states('sensor.sms_messages_sent').attributes.daily_count }} messages sent yesterday"
          target: "+1234567890"
          sender_id: "+1234567890"
```

## 🔍 Troubleshooting

### Counter Not Incrementing
1. Check that the entity exists: `input_number.sms_messages_sent` or `sensor.sms_messages_sent`
2. Verify SMS messages are being sent successfully
3. Check Home Assistant logs for any errors

### Data Not Persisting
1. Ensure the integration is properly configured
2. Check that the config entry is saved
3. Restart Home Assistant if needed

### Sensor Not Appearing
1. Restart Home Assistant after installing the integration
2. Check the integration is properly loaded
3. Verify the sensor appears in Developer Tools > States

## 📝 Notes

- **Automatic Tracking**: Counters increment automatically when SMS messages are sent successfully
- **Failed Messages**: Counters do not increment for failed SMS sends
- **Persistence**: Data is saved in the integration's config entry
- **Compatibility**: Works with all Home Assistant dashboard cards and automations
- **Performance**: Minimal impact on Home Assistant performance

## 🆘 Support

If you encounter issues with SMS tracking:

1. Check the [GitHub repository](https://github.com/oneofthegeeks/ha-goto) for updates
2. Enable debug logging for the integration
3. Check Home Assistant logs for error messages
4. Create an issue on GitHub with detailed information 