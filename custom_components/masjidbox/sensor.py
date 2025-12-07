from __future__ import annotations

from datetime import datetime
from typing import Any
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import MasjidBoxCoordinator
from .const import (
    COORDINATOR_KEY,
    DOMAIN,
    CONF_SLUG,
)


_LOGGER = logging.getLogger(__name__)

PRAYERS_ADHAN = [
    "fajr",
    "sunrise",
    "dhuhr",
    "asr",
    "maghrib",
    "isha",
]

PRAYERS_IQAMAH = [
    "fajr",
    "dhuhr",
    "asr",
    "maghrib",
    "isha",
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up MasjidBox sensors from a config entry."""
    entry_data: dict[str, Any] = entry.data
    slug: str = entry_data.get(CONF_SLUG, "")

    domain_data = hass.data[DOMAIN][entry.entry_id]
    coordinator: MasjidBoxCoordinator = domain_data[COORDINATOR_KEY]

    entities: list[SensorEntity] = []

    # Adhan sensors
    for prayer in PRAYERS_ADHAN:
        entities.append(
            MasjidBoxPrayerSensor(
                coordinator=coordinator,
                entry=entry,
                slug=slug,
                prayer=prayer,
                is_iqamah=False,
            )
        )

    # Iqamah sensors
    for prayer in PRAYERS_IQAMAH:
        entities.append(
            MasjidBoxPrayerSensor(
                coordinator=coordinator,
                entry=entry,
                slug=slug,
                prayer=prayer,
                is_iqamah=True,
            )
        )

    # Hijri date sensor
    entities.append(
        MasjidBoxHijriDateSensor(
            coordinator=coordinator,
            entry=entry,
            slug=slug,
        )
    )

    async_add_entities(entities)


def _parse_timestamp(value: str | None) -> datetime | None:
    """Parse API datetime string to tz-aware datetime."""
    if not value:
        return None
    try:
        # Replace trailing 'Z' with +00:00 to make it ISO 8601 with offset
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _get_today_data(data: dict[str, Any]) -> dict[str, Any] | None:
    """Return timetable[0] if present."""
    timetable = data.get("timetable")
    if not isinstance(timetable, list) or not timetable:
        _LOGGER.debug("MasjidBox sensor: no timetable[0] in coordinator data: %s", data)
        return None

    first = timetable[0]
    if not isinstance(first, dict):
        _LOGGER.debug("MasjidBox sensor: timetable[0] is not a dict: %s", first)
        return None

    return first


class MasjidBoxBaseEntity(CoordinatorEntity[MasjidBoxCoordinator], SensorEntity):
    """Base class for MasjidBox entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MasjidBoxCoordinator,
        entry: ConfigEntry,
        slug: str,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._slug = slug

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, slug)},
            name=f"MasjidBox ({slug})",
            manufacturer="MasjidBox",
        )

    @property
    def _today(self) -> dict[str, Any] | None:
        """Convenience accessor for today's data."""
        data = self.coordinator.data or {}
        return _get_today_data(data)


class MasjidBoxPrayerSensor(MasjidBoxBaseEntity):
    """Sensor for Adhan and Iqamah times."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(
        self,
        coordinator: MasjidBoxCoordinator,
        entry: ConfigEntry,
        slug: str,
        prayer: str,
        is_iqamah: bool,
    ) -> None:
        super().__init__(coordinator, entry, slug)
        self._prayer = prayer
        self._is_iqamah = is_iqamah

        kind = "Iqamah" if is_iqamah else "Adhan"
        self._attr_name = f"{kind} {prayer.capitalize()}"

        kind_key = "iqamah" if is_iqamah else "adhan"
        self._attr_unique_id = f"masjidbox_{slug}_{kind_key}_{prayer}"

    @property
    def native_value(self) -> datetime | None:
        """Return the adhan/iqamah time as a datetime."""
        today = self._today
        if not today:
            _LOGGER.debug("MasjidBox %s sensor has no 'today' data", self._attr_unique_id)
            return None

        if self._is_iqamah:
            iqamah = today.get("iqamah") or {}
            value = iqamah.get(self._prayer)
        else:
            value = today.get(self._prayer)

        if isinstance(value, list):
            # In case of lists (e.g. jumuah), use first element
            value = value[0] if value else None

        if not isinstance(value, str):
            _LOGGER.debug(
                "MasjidBox %s sensor has non-string value for %s: %s",
                self._attr_unique_id,
                self._prayer,
                value,
            )
            return None

        dt = _parse_timestamp(value)
        if dt is None:
            _LOGGER.debug(
                "MasjidBox %s sensor could not parse datetime from value %s",
                self._attr_unique_id,
                value,
            )

        return dt


class MasjidBoxHijriDateSensor(MasjidBoxBaseEntity):
    """Sensor for Hijri date (formatted)."""

    _attr_icon = "mdi:calendar-star"

    def __init__(
        self,
        coordinator: MasjidBoxCoordinator,
        entry: ConfigEntry,
        slug: str,
    ) -> None:
        super().__init__(coordinator, entry, slug)
        self._attr_name = "Hijri Date"
        self._attr_unique_id = f"masjidbox_{slug}_hijri_date"

    @property
    def native_value(self) -> str | None:
        """Return the formatted Hijri date."""
        today = self._today
        if not today:
            _LOGGER.debug("MasjidBox Hijri Date sensor has no 'today' data")
            return None

        hijri = today.get("hijri") or {}
        formatted = hijri.get("formatted")
        if not isinstance(formatted, str):
            _LOGGER.debug(
                "MasjidBox Hijri Date sensor has non-string formatted value: %s",
                formatted,
            )
            return None

        return formatted
