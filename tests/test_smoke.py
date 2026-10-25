from custom_components.energetyczny_kompas.calendar import (
    STATUS_MAPPING,
    EnergetycznyKompasCalendar,
)


def test_status_mapping_has_expected_values():
    assert STATUS_MAPPING[0] == "ZALECANE UŻYTKOWANIE"
    assert STATUS_MAPPING[1] == "NORMALNE UŻYTKOWANIE"
    assert STATUS_MAPPING[2] == "ZALECANE OSZCZĘDZANIE"
    assert STATUS_MAPPING[3] == "WYMAGANE OGRANICZANIE"


def test_parse_time_returns_timezone_aware_datetime():
    calendar = EnergetycznyKompasCalendar()

    parsed = calendar._parse_time("2024-12-20 00:00")
    assert parsed.tzinfo is not None
    assert parsed.year == 2024
    assert parsed.month == 12
    assert parsed.day == 20
    assert parsed.hour == 0

    parsed_plus_hour = calendar._parse_time("2024-12-20 00:00", add_hour=True)
    assert parsed_plus_hour.hour == 1
    assert parsed_plus_hour.tzinfo is not None


def test_calendar_has_default_state():
    calendar = EnergetycznyKompasCalendar()
    assert calendar.name == "Energetyczny Kompas"
    assert calendar.has_entity_name is True
    assert calendar.event is None
