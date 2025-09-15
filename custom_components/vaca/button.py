"""Wyoming button entities."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .custom import CustomActions
from .entity import VASatelliteEntity

if TYPE_CHECKING:
    from homeassistant.components.wyoming import DomainDataItem


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up switch entities."""
    item: DomainDataItem = hass.data[DOMAIN][config_entry.entry_id]

    # Setup is only forwarded for satellites
    assert item.device is not None

    async_add_entities(
        [
            WyomingSatelliteWakeButton(item.device),
            WyomingSatelliteRefreshButton(item.device),
            WyomingScreenWakeButton(item.device),
        ]
    )


class WyomingSatelliteWakeButton(VASatelliteEntity, ButtonEntity):
    """Entity to represent if satellite is muted."""

    entity_description = ButtonEntityDescription(
        key="wake",
        translation_key="wake",
    )

    async def async_press(self) -> None:
        """Press the button."""
        self._device.send_custom_action(CustomActions.WAKE)


class WyomingSatelliteRefreshButton(VASatelliteEntity, ButtonEntity):
    """Entity to represent if satellite is muted."""

    entity_description = ButtonEntityDescription(
        key="refresh",
        translation_key="refresh",
    )

    async def async_press(self) -> None:
        """Press the button."""
        self._device.send_custom_action(CustomActions.REFRESH)


class WyomingScreenWakeButton(VASatelliteEntity, ButtonEntity):
    """Entity to represent if screen is woken up."""

    entity_description = ButtonEntityDescription(
        key="screen_wake",
        translation_key="screen_wake",
    )

    async def async_press(self) -> None:
        """Press the button."""
        self._device.send_custom_action(CustomActions.SCREEN_WAKE)
