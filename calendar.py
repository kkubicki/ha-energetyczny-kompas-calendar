from datetime import datetime, timedelta
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.util import dt as dt_util
from .const import DOMAIN
import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)
URL = "https://data.energetycznykompas.pl/datafile/godzinyszczytu.json"

async def async_setup_entry(hass, config_entry, async_add_entities):
    async_add_entities([EnergetycznyKompasCalendar()])

class EnergetycznyKompasCalendar(CalendarEntity):

    def __init__(self):
        super().__init__()
        self._name = "Energetyczny Kompas"
        self._events: list[CalendarEvent] = []
        self._attr_unique_id = f"{DOMAIN}_calendar"
        self._attr_name = "Energetyczny Kompas calendar"

    @property
    def name(self):
        return self._name

    @property
    def has_entity_name(self):
        return True

    @property
    def event(self) -> CalendarEvent | None:
        now = dt_util.now()
        for event in self._events:
            if event.start <= now < event.end:
                return event
        return None

    async def async_get_events(
        self, hass, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        await self.async_update()
        return [
            event
            for event in self._events
            if start_date <= event.start < end_date
        ]

    async def async_update(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(URL) as response:
                    response.raise_for_status()
                    data = await response.json()

            self._events = [
                CalendarEvent(
                    summary=f"Status: {entry['status']}",
                    start=self._format_time(entry["data"], entry["godzina"]),
                    end=self._format_time(entry["data"], entry["godzina"] + 1),
                    description=f"Zapotrzebowanie: {entry['zapotrzebowanie']} MW",
                )
                for entry in data
            ]
        except Exception as e:
            _LOGGER.error("Error fetching data from Energetyczny Kompas: %s", e)
            self._events = []

    def _format_time(self, date_str, hour):
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")

        if hour == 24:
            date_obj += timedelta(days=1)
            hour = 0

        return date_obj.replace(hour=hour, tzinfo=dt_util.DEFAULT_TIME_ZONE)
