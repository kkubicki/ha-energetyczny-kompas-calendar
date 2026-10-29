from __future__ import annotations

import logging
from datetime import datetime, timedelta

import aiohttp
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=30)

URL = "https://api.raporty.pse.pl/api/pdgsz?$filter=dtime%20gt%20'{}'%20and%20is_active%20eq%20true"

STATUS_MAPPING = {
    0: "ZALECANE UŻYTKOWANIE",
    1: "NORMALNE UŻYTKOWANIE",
    2: "ZALECANE OSZCZĘDZANIE",
    3: "WYMAGANE OGRANICZANIE",
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Energetyczny Kompas calendar entity."""
    async_add_entities([EnergetycznyKompasCalendar()], update_before_add=True)


class EnergetycznyKompasCalendar(CalendarEntity):
    """Calendar entity for Energetyczny Kompas."""

    _attr_has_entity_name = True
    _attr_name = "Energetyczny Kompas"
    _attr_unique_id = f"{DOMAIN}_calendar"

    def __init__(self) -> None:
        """Initialize the calendar."""
        super().__init__()
        self._events: list[CalendarEvent] = []

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming or currently active event."""
        now = dt_util.now()
        # Return currently active event if one exists
        for event in self._events:
            if event.start <= now < event.end:
                return event

        # Otherwise return the nearest upcoming event
        upcoming_events = [e for e in self._events if e.start >= now]
        if upcoming_events:
            return min(upcoming_events, key=lambda e: e.start)

        return None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        if not self._events:
            await self.async_update()

        return [
            event
            for event in self._events
            if event.end > start_date and event.start < end_date
        ]

    async def async_update(self) -> None:
        """Fetch latest data from PSE API."""
        formatted_date = (dt_util.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        url = URL.format(formatted_date)
        session = async_get_clientsession(self.hass)

        try:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response.raise_for_status()
                data = await response.json()
        except (TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.warning("Error fetching data from PSE API: %s", err)
            return
        except Exception:
            _LOGGER.exception("Unexpected error fetching data from PSE API")
            return

        values = data.get("value")
        if not isinstance(values, list):
            _LOGGER.warning("Unexpected data format from PSE API: missing 'value' list")
            return

        events: list[CalendarEvent] = []
        for entry in values:
            dtime_utc = entry.get("dtime_utc")
            usage_fcst = entry.get("usage_fcst")
            if not dtime_utc or usage_fcst is None:
                continue

            try:
                start_time = self._parse_time(dtime_utc)
                end_time = self._parse_time(dtime_utc, add_hour=True)
            except (ValueError, TypeError) as err:
                _LOGGER.debug("Skipping unparseable PSE entry %s: %s", entry, err)
                continue

            summary = f"Status: {STATUS_MAPPING.get(usage_fcst, 'NIEZNANY STATUS')}"
            events.append(
                CalendarEvent(
                    summary=summary,
                    start=start_time,
                    end=end_time,
                    description=str(usage_fcst),
                )
            )

        events.sort(key=lambda ev: ev.start)
        self._events = events

    def _parse_time(self, timestamp: str, add_hour: bool = False) -> datetime:
        """Parse PSE UTC timestamp and convert to local timezone."""
        date_obj = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
        date_obj = date_obj.replace(tzinfo=dt_util.UTC)

        if add_hour:
            date_obj += timedelta(hours=1)

        return date_obj.astimezone(dt_util.DEFAULT_TIME_ZONE)
