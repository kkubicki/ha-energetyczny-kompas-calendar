from __future__ import annotations

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
from homeassistant.components.calendar import CalendarEvent
from homeassistant.util import dt as dt_util

from custom_components.energetyczny_kompas.calendar import (
    STATUS_MAPPING,
    EnergetycznyKompasCalendar,
)


def test_status_mapping() -> None:
    """Test that STATUS_MAPPING has expected entries."""
    assert STATUS_MAPPING[0] == "ZALECANE UŻYTKOWANIE"
    assert STATUS_MAPPING[1] == "NORMALNE UŻYTKOWANIE"
    assert STATUS_MAPPING[2] == "ZALECANE OSZCZĘDZANIE"
    assert STATUS_MAPPING[3] == "WYMAGANE OGRANICZANIE"


def test_parse_time() -> None:
    """Test _parse_time creates correct timezone-aware datetimes."""
    calendar = EnergetycznyKompasCalendar()

    dt_start = calendar._parse_time("2026-10-29 10:00")
    assert dt_start.tzinfo is not None

    dt_end = calendar._parse_time("2026-10-29 10:00", add_hour=True)
    assert dt_end - dt_start == timedelta(hours=1)


def test_event_property_selection() -> None:
    """Test event property returns active event or nearest upcoming event."""
    calendar = EnergetycznyKompasCalendar()
    assert calendar.event is None

    now = dt_util.now()

    past_event = CalendarEvent(
        start=now - timedelta(hours=2),
        end=now - timedelta(hours=1),
        summary="Past",
    )
    active_event = CalendarEvent(
        start=now - timedelta(minutes=30),
        end=now + timedelta(minutes=30),
        summary="Active",
    )
    upcoming_event_1 = CalendarEvent(
        start=now + timedelta(hours=1),
        end=now + timedelta(hours=2),
        summary="Upcoming 1",
    )
    upcoming_event_2 = CalendarEvent(
        start=now + timedelta(hours=3),
        end=now + timedelta(hours=4),
        summary="Upcoming 2",
    )

    # Active event present
    calendar._events = [past_event, active_event, upcoming_event_1, upcoming_event_2]
    assert calendar.event == active_event

    # No active event, but upcoming events exist -> return earliest upcoming
    calendar._events = [past_event, upcoming_event_2, upcoming_event_1]
    assert calendar.event == upcoming_event_1

    # Only past events exist -> None
    calendar._events = [past_event]
    assert calendar.event is None


@pytest.mark.asyncio
async def test_async_get_events_overlap() -> None:
    """Test async_get_events includes events overlapping the time range."""
    calendar = EnergetycznyKompasCalendar()
    t0 = dt_util.now()

    # Event 1: starts before window, ends inside window
    ev1 = CalendarEvent(start=t0, end=t0 + timedelta(hours=2), summary="Overlap Start")
    # Event 2: completely inside window
    ev2 = CalendarEvent(
        start=t0 + timedelta(hours=2),
        end=t0 + timedelta(hours=3),
        summary="Inside",
    )
    # Event 3: starts inside window, ends after window
    ev3 = CalendarEvent(
        start=t0 + timedelta(hours=3),
        end=t0 + timedelta(hours=5),
        summary="Overlap End",
    )
    # Event 4: completely before window
    ev4 = CalendarEvent(
        start=t0 - timedelta(hours=3),
        end=t0 - timedelta(hours=1),
        summary="Before",
    )
    # Event 5: completely after window
    ev5 = CalendarEvent(
        start=t0 + timedelta(hours=6),
        end=t0 + timedelta(hours=7),
        summary="After",
    )

    calendar._events = [ev1, ev2, ev3, ev4, ev5]

    # Query range from t0 + 1 hour to t0 + 4 hours
    range_start = t0 + timedelta(hours=1)
    range_end = t0 + timedelta(hours=4)

    events = await calendar.async_get_events(MagicMock(), range_start, range_end)
    assert ev1 in events
    assert ev2 in events
    assert ev3 in events
    assert ev4 not in events
    assert ev5 not in events


@pytest.mark.asyncio
async def test_async_update_success() -> None:
    """Test async_update parses PSE payload and sorts events."""
    calendar = EnergetycznyKompasCalendar()
    mock_hass = MagicMock()
    calendar.hass = mock_hass

    api_payload = {
        "value": [
            {
                "dtime_utc": "2026-10-29 11:00",
                "usage_fcst": 1,
            },
            {
                "dtime_utc": "2026-10-29 10:00",
                "usage_fcst": 0,
            },
        ]
    }

    mock_resp = AsyncMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json = AsyncMock(return_value=api_payload)

    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = mock_resp

    with patch(
        "custom_components.energetyczny_kompas.calendar.async_get_clientsession",
        return_value=mock_session,
    ):
        await calendar.async_update()

    assert len(calendar._events) == 2
    # Verify sorted by start time
    assert calendar._events[0].summary == "Status: ZALECANE UŻYTKOWANIE"
    assert calendar._events[1].summary == "Status: NORMALNE UŻYTKOWANIE"


@pytest.mark.asyncio
async def test_async_update_network_error_retains_events() -> None:
    """Test async_update does not wipe events on network error."""
    calendar = EnergetycznyKompasCalendar()
    mock_hass = MagicMock()
    calendar.hass = mock_hass

    existing_event = CalendarEvent(
        start=dt_util.now(),
        end=dt_util.now() + timedelta(hours=1),
        summary="Existing",
    )
    calendar._events = [existing_event]

    mock_session = MagicMock()
    mock_session.get.side_effect = aiohttp.ClientConnectionError("Network down")

    with patch(
        "custom_components.energetyczny_kompas.calendar.async_get_clientsession",
        return_value=mock_session,
    ):
        await calendar.async_update()

    # Events should be retained, not wiped
    assert calendar._events == [existing_event]


@pytest.mark.asyncio
async def test_async_update_skips_malformed_entries() -> None:
    """Test async_update skips null or non-dict items and processes valid ones."""
    calendar = EnergetycznyKompasCalendar()
    mock_hass = MagicMock()
    calendar.hass = mock_hass

    api_payload = {
        "value": [
            None,
            "not a dict",
            123,
            {"dtime_utc": "2026-10-29 10:00", "usage_fcst": 0},
            {"dtime_utc": None, "usage_fcst": 1},
            {"invalid_keys": True},
        ]
    }

    mock_resp = AsyncMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json = AsyncMock(return_value=api_payload)

    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = mock_resp

    with patch(
        "custom_components.energetyczny_kompas.calendar.async_get_clientsession",
        return_value=mock_session,
    ):
        await calendar.async_update()

    assert len(calendar._events) == 1
    assert calendar._events[0].summary == "Status: ZALECANE UŻYTKOWANIE"


@pytest.mark.asyncio
async def test_async_update_invalid_top_level_payload() -> None:
    """Test async_update handles non-dict top level responses gracefully."""
    calendar = EnergetycznyKompasCalendar()
    mock_hass = MagicMock()
    calendar.hass = mock_hass

    existing_event = CalendarEvent(
        start=dt_util.now(),
        end=dt_util.now() + timedelta(hours=1),
        summary="Existing",
    )
    calendar._events = [existing_event]

    mock_resp = AsyncMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json = AsyncMock(return_value=["not", "a", "dict"])

    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = mock_resp

    with patch(
        "custom_components.energetyczny_kompas.calendar.async_get_clientsession",
        return_value=mock_session,
    ):
        await calendar.async_update()

    # Should retain existing events rather than crashing
    assert calendar._events == [existing_event]
