from __future__ import annotations

import logging
from typing import Any

from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from aiohttp import ClientError, ClientSession
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.typing import ConfigType

from .const import (
    API_URL,
    COORDINATOR_KEY,
    DEFAULT_DAYS,
    DOMAIN,
    PLATFORMS,
    CONF_SLUG,
    CONF_APIKEY,
    CONF_DAYS,
)

_LOGGER = logging.getLogger(__name__)

type MasjidBoxConfigEntry = ConfigEntry


class MasjidBoxCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to fetch data from the MasjidBox API."""

    def __init__(
        self,
        hass: HomeAssistant,
        session: ClientSession,
        entry: MasjidBoxConfigEntry,
    ) -> None:
        self.hass = hass
        self._session = session
        self._entry = entry

        data = entry.data
        self._slug: str = data.get(CONF_SLUG, "")
        self._apikey: str = data.get(CONF_APIKEY, data.get(CONF_API_KEY, ""))
        self._days: int = data.get(CONF_DAYS, DEFAULT_DAYS)

        super().__init__(
            hass,
            _LOGGER,
            name=f"MasjidBox {self._slug}",
            update_interval=timedelta(minutes=60),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from MasjidBox API."""
        # Compute today's midnight in UTC with milliseconds and +00:00
        now_utc = datetime.now(timezone.utc)
        midnight_utc = datetime(
            year=now_utc.year,
            month=now_utc.month,
            day=now_utc.day,
            tzinfo=timezone.utc,
        )
        begin = midnight_utc.isoformat(timespec="milliseconds")
        # The MasjidBox API expects an encoded begin parameter (see cURL example),
        # otherwise the '+' and ':' characters can break parsing and result in
        # 'Invalid date' values in the timetable.
        encoded_begin = quote(begin, safe="")

        url = API_URL.format(
            slug=self._slug,
            days=self._days,
            begin=encoded_begin,
        )

        headers = {
            "apikey": self._apikey,
        }

        _LOGGER.debug("Requesting MasjidBox data from %s", url)

        try:
            async with self._session.get(url, headers=headers, timeout=30) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise UpdateFailed(
                        f"Error fetching MasjidBox data: HTTP {resp.status} - {text}"
                    )

                data = await resp.json()
        except (ClientError, TimeoutError) as err:
            raise UpdateFailed(f"Error communicating with MasjidBox API: {err}") from err
        except Exception as err:  # pragma: no cover - defensive
            raise UpdateFailed(f"Unexpected error from MasjidBox API: {err}") from err

        if not isinstance(data, dict):
            raise UpdateFailed("Invalid data from MasjidBox API (expected JSON object)")

        _LOGGER.debug("MasjidBox API response for slug %s: %s", self._slug, data)

        return data


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the MasjidBox component (YAML not supported)."""
    # UI config flow only; nothing to set up from YAML
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up MasjidBox from a config entry."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    session = async_get_clientsession(hass)

    coordinator = MasjidBoxCoordinator(hass, session, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        COORDINATOR_KEY: coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(
        entry,
        [Platform.SENSOR],
    )

    _LOGGER.debug("MasjidBox entry setup completed for slug %s", entry.data.get(CONF_SLUG))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a MasjidBox config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, [Platform.SENSOR])

    if unload_ok:
        domain_data = hass.data.get(DOMAIN, {})
        domain_data.pop(entry.entry_id, None)
        if not domain_data:
            hass.data.pop(DOMAIN, None)

    return unload_ok
