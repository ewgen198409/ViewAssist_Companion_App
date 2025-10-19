"""Wyoming switch entities."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers import restore_state
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .entity import VASatelliteEntity

if TYPE_CHECKING:
    from homeassistant.components.wyoming import DomainDataItem

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up switch entities."""
    item: DomainDataItem = hass.data[DOMAIN][config_entry.entry_id]

    # Setup is only forwarded for satellites
    assert item.device is not None
    entities = [
        WyomingSatelliteMuteSwitch(item.device),
        WyomingSatelliteSwipeToRefreshSwitch(item.device),
        WyomingSatelliteScreenAutoBrightnessSwitch(item.device),
        WyomingSatelliteScreenAlwaysOnSwitch(item.device),
        WyomingSatelliteDarkModeSwitch(item.device),
        WyomingSatelliteDiagnosticsSwitch(item.device),
        WyomingSatelliteContinueConversationSwitch(item.device),
        WyomingSatelliteAlarmSwitch(item.device),
    ]

    if capabilities := item.device.capabilities:
        if capabilities.get("has_dnd"):
            entities.append(WyomingSatelliteDNDSwitch(item.device))

    if entities:
        async_add_entities(entities)


class BaseSwitch(VASatelliteEntity, restore_state.RestoreEntity, SwitchEntity):
    """Base class for all switch entities."""

    entity_description: SwitchEntityDescription
    default_on = False

    async def async_added_to_hass(self) -> None:
        """Call when entity about to be added to hass."""
        await super().async_added_to_hass()

        state = await self.async_get_last_state()

        # Set restore state or default
        if self.default_on:
            self._attr_is_on = (state is None) or (state.state == STATE_ON)
        else:
            self._attr_is_on = (state is not None) and (state.state == STATE_ON)

        await self.do_switch(self._attr_is_on)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on."""
        await self.do_switch(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off."""
        await self.do_switch(False)

    async def do_switch(self, value: bool) -> None:
        """Perform the switch action."""
        self._attr_is_on = value
        self.async_write_ha_state()
        self._device.set_custom_setting(self.entity_description.key, self._attr_is_on)


class WyomingSatelliteMuteSwitch(BaseSwitch):
    """Entity to represent if satellite is muted."""

    entity_description = SwitchEntityDescription(key="mute", translation_key="mute")
    default_on = False

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend."""
        return "mdi:microphone-off" if self._attr_is_on else "mdi:microphone"


class WyomingSatelliteSwipeToRefreshSwitch(BaseSwitch):
    """Entity to control swipe to refresh."""

    entity_description = SwitchEntityDescription(
        key="swipe_refresh",
        translation_key="swipe_refresh",
        icon="mdi:web-refresh",
        entity_category=EntityCategory.CONFIG,
    )
    default_on = True


class WyomingSatelliteScreenAutoBrightnessSwitch(BaseSwitch):
    """Entity to control swipe to refresh."""

    entity_description = SwitchEntityDescription(
        key="screen_auto_brightness",
        translation_key="screen_auto_brightness",
        icon="mdi:monitor-screenshot",
        entity_category=EntityCategory.CONFIG,
    )
    default_on = True


class WyomingSatelliteScreenAlwaysOnSwitch(BaseSwitch):
    """Entity to control screen always on."""

    entity_description = SwitchEntityDescription(
        key="screen_always_on",
        translation_key="screen_always_on",
        icon="mdi:monitor-screenshot",
        entity_category=EntityCategory.CONFIG,
    )
    default_on = True


class WyomingSatelliteDarkModeSwitch(BaseSwitch):
    """Entity to control screen always on."""

    entity_description = SwitchEntityDescription(
        key="dark_mode",
        translation_key="dark_mode",
        icon="mdi:compare",
        entity_category=EntityCategory.CONFIG,
    )
    default_on = False


class WyomingSatelliteDNDSwitch(BaseSwitch):
    """Entity to control screen always on."""

    entity_description = SwitchEntityDescription(
        key="do_not_disturb",
        translation_key="do_not_disturb",
        icon="mdi:do-not-disturb",
    )
    default_on = False


class WyomingSatelliteDiagnosticsSwitch(BaseSwitch):
    """Entity to control diagnostics overlay on/off."""

    entity_description = SwitchEntityDescription(
        key="diagnostics_enabled",
        translation_key="diagnostics_enabled",
        icon="mdi:microphone-question",
        entity_category=EntityCategory.DIAGNOSTIC,
    )
    default_on = False


class WyomingSatelliteContinueConversationSwitch(BaseSwitch):
    """Entity to control continue conversation on/off."""

    entity_description = SwitchEntityDescription(
        key="continue_conversation",
        translation_key="continue_conversation",
        icon="mdi:message-bulleted",
        entity_category=EntityCategory.CONFIG,
    )
    default_on = True


class WyomingSatelliteAlarmSwitch(BaseSwitch):
    """Entity to control alarm on/off."""

    entity_description = SwitchEntityDescription(
        key="alarm",
        translation_key="alarm",
        icon="mdi:alarm-bell",
    )
    default_on = False

    async def do_switch(self, value: bool) -> None:
        """Perform the switch action."""
        self._attr_is_on = value
        self.async_write_ha_state()
        self._device.send_custom_action(
            self.entity_description.key, {"activate": self._attr_is_on}
        )
