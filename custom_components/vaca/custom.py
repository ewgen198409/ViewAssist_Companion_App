"""# Custom components for View Assist satellite integration with Wyoming events."""

from dataclasses import dataclass
from enum import StrEnum
import logging
from typing import Any

from wyoming.event import Event, Eventable

_LOGGER = logging.getLogger(__name__)

_CUSTOM_EVENT_TYPE = "custom-event"

ACTION_EVENT_TYPE = "action"
CAPABILITIES_EVENT_TYPE = "capabilities"
SETTINGS_EVENT_TYPE = "settings"


class CustomActions(StrEnum):
    """Actions for media control."""

    TOAST_MESSAGE = "toast-message"
    MEDIA_PLAY_MEDIA = "play-media"
    MEDIA_PLAY = "play"
    MEDIA_PAUSE = "pause"
    MEDIA_STOP = "stop"
    MEDIA_SET_VOLUME = "set-volume"


@dataclass
class CustomEvent(Eventable):
    """Custom event class."""

    event_type: str
    """Type of the event."""

    event_data: dict[str, Any] | None = None
    """Data associated with the event."""

    @staticmethod
    def is_type(event_type: str) -> bool:
        """Check if the event type matches."""
        return event_type == _CUSTOM_EVENT_TYPE

    def event(self) -> Event:
        """Create an event for the custom event."""
        data = {"event_type": self.event_type}
        if self.event_data is not None:
            data.update(self.event_data)
        return Event(
            type=_CUSTOM_EVENT_TYPE,
            data=data,
        )

    @staticmethod
    def from_event(event: Event) -> "CustomEvent":
        """Create a CustomEvent instance from an event."""
        return CustomEvent(
            event_type=event.data.get("event_type"), event_data=event.data.get("data")
        )


@dataclass
class CustomStatus(Eventable):
    """Custom sensor value event."""

    data: Any
    """Value of the sensor."""

    @staticmethod
    def is_type(event_type: str) -> bool:
        """Check if the event type is a custom sensor value event."""
        return event_type == "custom-status"

    def event(self) -> Event:
        """Create an event for custom sensor value."""
        return Event(
            type="custom-status",
            data=self.data,
        )

    @staticmethod
    def from_event(event: Event) -> "CustomStatus":
        """Create a CustomSensorValue instance from an event."""
        return CustomStatus(data=event.data)


@dataclass
class CustomCapabilities(Eventable):
    """Custom capabilities event."""

    capabilities: Any | None = None

    @staticmethod
    def is_type(event_type: str) -> bool:
        """Check if the event type is a custom capabilities event."""
        return event_type == "capabilities"

    def event(self) -> Event:
        """Create an event for custom describe."""
        return Event(type="capabilities")

    @staticmethod
    def from_event(event: Event) -> "CustomCapabilities":
        """Create a CustomCapabilities instance from an event."""
        return CustomCapabilities(capabilities=event.data)
