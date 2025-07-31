"""SMS Message Counter Sensor for GoTo SMS integration."""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the SMS message counter sensor."""
    _LOGGER.info("Setting up SMS message counter sensor")

    # Create the sensor
    sensor = SMSMessageCounterSensor(config_entry)
    async_add_entities([sensor], True)


class SMSMessageCounterSensor(SensorEntity):
    """Sensor that tracks SMS messages sent."""

    def __init__(self, config_entry: ConfigEntry):
        """Initialize the sensor."""
        self.config_entry = config_entry
        self._attr_name = f"SMS Messages Sent"
        self._attr_unique_id = f"{config_entry.entry_id}_sms_counter"
        self._attr_native_value = 0
        self._attr_native_unit_of_measurement = "messages"
        self._attr_icon = "mdi:message-text"

        # Initialize counters
        self._daily_count = 0
        self._weekly_count = 0
        self._monthly_count = 0
        self._total_count = 0
        self._last_reset_date = datetime.now().date()

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        return {
            "daily_count": self._daily_count,
            "weekly_count": self._weekly_count,
            "monthly_count": self._monthly_count,
            "total_count": self._total_count,
            "last_reset": self._last_reset_date.isoformat(),
            "friendly_name": "SMS Messages Sent",
            "icon": "mdi:message-text",
        }

    def increment_counter(self) -> None:
        """Increment the message counter."""
        current_date = datetime.now().date()

        # Reset daily counter if it's a new day
        if current_date != self._last_reset_date:
            self._daily_count = 0
            self._last_reset_date = current_date

            # Reset weekly counter if it's been more than 7 days
            if (current_date - self._last_reset_date).days >= 7:
                self._weekly_count = 0

            # Reset monthly counter if it's been more than 30 days
            if (current_date - self._last_reset_date).days >= 30:
                self._monthly_count = 0

        # Increment all counters
        self._daily_count += 1
        self._weekly_count += 1
        self._monthly_count += 1
        self._total_count += 1
        self._attr_native_value = self._total_count

        # Schedule state update
        self.async_write_ha_state()
        _LOGGER.info(f"SMS message counter incremented. Total: {self._total_count}")

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        # Load saved state if available
        if self.config_entry.data.get("sms_counter"):
            counter_data = self.config_entry.data["sms_counter"]
            self._daily_count = counter_data.get("daily", 0)
            self._weekly_count = counter_data.get("weekly", 0)
            self._monthly_count = counter_data.get("monthly", 0)
            self._total_count = counter_data.get("total", 0)
            self._attr_native_value = self._total_count
            _LOGGER.info(
                f"Loaded SMS counter state: {self._total_count} total messages"
            )

    def save_state(self) -> None:
        """Save the current state to config entry."""
        try:
            # Update the config entry with counter data
            data = dict(self.config_entry.data)
            data["sms_counter"] = {
                "daily": self._daily_count,
                "weekly": self._weekly_count,
                "monthly": self._monthly_count,
                "total": self._total_count,
                "last_reset": self._last_reset_date.isoformat(),
            }

            # Schedule the update
            self.hass.async_create_task(
                self.hass.config_entries.async_update_entry(
                    self.config_entry, data=data
                )
            )
        except Exception as e:
            _LOGGER.error(f"Failed to save SMS counter state: {e}")
