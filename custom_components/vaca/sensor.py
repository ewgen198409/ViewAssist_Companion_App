"""Sensor for Wyoming."""

from __future__ import annotations

from functools import reduce
import json
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import RestoreSensor, SensorEntityDescription
from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import LIGHT_LUX, PERCENTAGE, EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .entity import VASatelliteEntity

if TYPE_CHECKING:
    from homeassistant.components.wyoming import DomainDataItem

UNKNOWN: str = "unknown"

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up sensor entities."""
    item: DomainDataItem = hass.data[DOMAIN][config_entry.entry_id]

    # Setup is only forwarded for satellites
    assert item.device is not None

    entities = [
        WyomingSatelliteSTTSensor(item.device),
        WyomingSatelliteTTSSensor(item.device),
        WyomingSatelliteIntentSensor(item.device),
        WyomingSatelliteOrientationSensor(item.device),
    ]

    if capabilities := item.device.capabilities:
        if capabilities.get("app_version"):
            entities.append(WyomingSatelliteAppVersionSensor(item.device))
        if capabilities.get("has_battery"):
            entities.append(WyomingSatelliteBatteryLevelSensor(item.device))
            entities.append(WyomingSatelliteBatteryChargingSensor(item.device))
        if item.device.has_light_sensor():
            entities.append(WyomingSatelliteLightSensor(item.device))

    async_add_entities(entities)


class WyomingSatelliteSTTSensor(VASatelliteEntity, RestoreSensor):
    """Entity to represent STT sensor for satellite."""

    entity_description = SensorEntityDescription(
        key="stt",
        translation_key="stt",
        icon="mdi:microphone-message",
    )
    _attr_native_value = UNKNOWN

    async def async_added_to_hass(self) -> None:
        """Call when entity about to be added to hass."""
        await super().async_added_to_hass()

        state = await self.async_get_last_state()
        if state is not None:
            self._value_changed(state.state)

        self._device.set_stt_listener(self._value_changed)

    @callback
    def _value_changed(self, value: str) -> None:
        """Call when value changed."""
        if value:
            if len(value) > 254:
                # Limit the length of the value to avoid issues with Home Assistant
                value = value[:252] + ".."
            self._attr_native_value = value
            self.async_write_ha_state()


class WyomingSatelliteTTSSensor(VASatelliteEntity, RestoreSensor):
    """Entity to represent TTS sensor for satellite."""

    entity_description = SensorEntityDescription(
        key="tts", translation_key="tts", icon="mdi:speaker-message"
    )
    _attr_native_value = UNKNOWN

    async def async_added_to_hass(self) -> None:
        """Call when entity about to be added to hass."""
        await super().async_added_to_hass()

        state = await self.async_get_last_state()
        if state is not None:
            self._value_changed(state.state)

        self._device.set_tts_listener(self._value_changed)

    @callback
    def _value_changed(self, value: str) -> None:
        """Call when value changed."""
        if value:
            if len(value) > 254:
                # Limit the length of the value to avoid issues with Home Assistant
                value = value[:252] + ".."
            self._attr_native_value = value
            self.async_write_ha_state()


class WyomingSatelliteIntentSensor(VASatelliteEntity, RestoreSensor):
    """Entity to represent intent sensor for satellite."""

    entity_description = SensorEntityDescription(
        key="intent", translation_key="intent", icon="mdi:message-bulleted"
    )
    _attr_native_value = 0

    async def async_added_to_hass(self) -> None:
        """Call when entity about to be added to hass."""
        await super().async_added_to_hass()

        state = await self.async_get_last_state()
        if state is not None:
            self._attr_native_value = state.state
            self.async_write_ha_state()

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{DOMAIN}_{self._device.device_id}_intent_output",
                self.status_update,
            )
        )

    @callback
    def status_update(self, data: dict[str, Any]) -> None:
        """Update entity."""
        if data and data.get("intent_output"):
            self._attr_native_value = self.get_key(
                "intent_output.response.speech.plain.speech", data
            )
            self._attr_extra_state_attributes = data
            self.async_write_ha_state()

    def get_key(
        self, dot_notation_path: str, data: dict
    ) -> dict[str, dict | str | int] | str | int:
        """Try to get a deep value from a dict based on a dot-notation."""

        try:
            if "." in dot_notation_path:
                dn_list = dot_notation_path.split(".")
            else:
                dn_list = [dot_notation_path]
            return reduce(dict.get, dn_list, data)
        except (TypeError, KeyError):
            return None


class _WyomingSatelliteDeviceSensorBase(VASatelliteEntity, RestoreSensor):
    """Base class for device sensors."""

    _attr_native_value = 0
    _listener_class = "status_update"

    async def async_added_to_hass(self) -> None:
        """Call when entity about to be added to hass."""
        await super().async_added_to_hass()

        state = await self.async_get_last_state()
        if state is not None:
            self._attr_native_value = state.state
            self.async_write_ha_state()

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{DOMAIN}_{self._device.device_id}_{self._listener_class}",
                self.status_update,
            )
        )

    def _get_native_value(self, value: Any) -> Any:
        """Get the native value from the data."""
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str):
            if value.isdigit():
                return int(value)
            return value
        return value

    @callback
    def status_update(self, data: dict[str, Any]) -> None:
        """Update entity."""
        if self._listener_class == "status_update":
            if sensors := data.get("sensors"):
                if self.entity_description.key in sensors:
                    self._attr_native_value = self._get_native_value(
                        sensors[self.entity_description.key]
                    )
                    self.async_write_ha_state()
        elif self._listener_class == "capabilities_update":
            if self._device.capabilities.get(self.entity_description.key):
                self._attr_native_value = self._get_native_value(
                    self._device.capabilities[self.entity_description.key]
                )
                self.async_write_ha_state()


class WyomingSatelliteLightSensor(_WyomingSatelliteDeviceSensorBase):
    """Entity to represent light sensor for satellite."""

    entity_description = SensorEntityDescription(
        key="light",
        translation_key="light_level",
        device_class=SensorDeviceClass.ILLUMINANCE,
        native_unit_of_measurement=LIGHT_LUX,
    )


class WyomingSatelliteOrientationSensor(_WyomingSatelliteDeviceSensorBase):
    """Entity to represent orientation sensor for satellite."""

    _attr_native_value = UNKNOWN
    entity_description = SensorEntityDescription(
        key="orientation", translation_key="orientation", icon="mdi:screen-rotation"
    )


class WyomingSatelliteBatteryLevelSensor(_WyomingSatelliteDeviceSensorBase):
    """Entity to represent battery level sensor for satellite."""

    entity_description = SensorEntityDescription(
        key="battery_level",
        translation_key="battery_level",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
    )


class WyomingSatelliteBatteryChargingSensor(_WyomingSatelliteDeviceSensorBase):
    """Entity to represent battery charging sensor for satellite."""

    _attr_native_value = UNKNOWN
    entity_description = SensorEntityDescription(
        key="battery_charging",
        translation_key="battery_charging",
        icon="mdi:battery-charging",
    )

    def _get_native_value(self, value: Any) -> Any:
        """Get the native value from the data."""
        return "not_charging" if int(value) == 0 else "charging"


class WyomingSatelliteAppVersionSensor(_WyomingSatelliteDeviceSensorBase):
    """Entity to represent app version sensor for satellite."""

    _listener_class = "capabilities_update"
    _attr_native_value = UNKNOWN
    entity_description = SensorEntityDescription(
        key="app_version",
        translation_key="app_version",
        icon="mdi:application",
        entity_category=EntityCategory.DIAGNOSTIC,
        name="App version",
    )

    def _get_native_value(self, value: Any) -> Any:
        """Get the native value from the data."""
        return value if value is not None else UNKNOWN

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity attributes."""
        return {
            "device_signature": self.get_capability("device_signature"),
            "android_version": self.get_capability("release"),
            "has_battery": self.get_capability("has_battery"),
            "has_front_camera": self.get_capability("has_front_camera"),
            "has_light_sensor": self._device.has_light_sensor(),
            "sensors": self.get_sensor_names(),
        }

    def get_capability(self, capability: str) -> Any:
        """Get a specific capability from the device."""
        return self._device.capabilities.get(capability, UNKNOWN)

    def get_sensor_names(self) -> list[str]:
        """Get the names of all sensors."""
        if sensors := self._device.capabilities.get("sensors"):
            return [json.loads(sensor).get("name") for sensor in sensors]
        return None
