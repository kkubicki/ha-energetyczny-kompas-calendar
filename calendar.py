from datetime import datetime, timedelta
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.util import dt as dt_util
from .const import DOMAIN
import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)
URL = "https://api.raporty.pse.pl/api/pdgsz?$filter=dtime%20gt%20'{}'%20and%20is_active%20eq%20true"

STATUS_MAPPING = {
    0: "ZALECANE UŻYTKOWANIE",
    1: "NORMALNE UŻYTKOWANIE",
    2: "ZALECANE OSZCZĘDZANIE",
    3: "WYMAGANE OGRANICZANIE",
}

async def async_setup_entry(hass, config_entry, async_add_entities):
    async_add_entities([EnergetycznyKompasCalendar()])

class EnergetycznyKompasCalendar(CalendarEntity):

    def __init__(self):
        super().__init__()
        self._name = "Energetyczny Kompas"
        self._events: list[CalendarEvent] = []
        self._attr_unique_id = f"{DOMAIN}_calendar"
        self._attr_name = "Energetyczny Kompas Calendar"

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
            formatted_date = dt_util.now().strftime("%Y-%m-%d")
            url = URL.format(formatted_date)

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()

            self._events = [
                CalendarEvent(
                    summary=f"Status: {STATUS_MAPPING.get(entry['usage_fcst'], 'NIEZNANY STATUS')}",
                    start=self._parse_time(entry["dtime"]),
                    end=self._parse_time(entry["dtime"], add_hour=True),
                    description=f"{entry['usage_fcst']}",
                )
                for entry in data["value"]
            ]
        except Exception as e:
            _LOGGER.error("Error fetching data from PSE API: %s", e)
            self._events = []

    def _parse_time(self, timestamp: str, add_hour: bool = False) -> datetime:
        date_obj = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")

        if add_hour:
            date_obj += timedelta(hours=1)

        return date_obj.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)
