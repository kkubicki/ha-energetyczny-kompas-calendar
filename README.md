# Energetyczny Kompas Calendar
![Energetyczny Kompas logo](logo.png)

**Energetyczny Kompas Calendar** is a Home Assistant custom integration that fetches electricity demand forecasts from the [PSE API](https://api.raporty.pse.pl/) and displays usage recommendations in your Home Assistant calendar.

## Installation

1. **Add to HACS**:
   - Open HACS in Home Assistant.
   - Click on the "..." button and add this repository (https://github.com/kkubicki/ha-energetyczny-kompas-calendar) as a custom repository.

2. **Install the Integration**:
   - Search for "Energetyczny Kompas Calendar" in HACS and install it.

3. **Restart Home Assistant**:
   - Restart your Home Assistant to load the component.

4. **Configure**:
   - Add the integration via Home Assistant → Settings → Devices & Services → Add Integration → "Energetyczny Kompas Calendar."

## Usage

Once installed, this component will:
- Fetch electricity demand forecasts from the PSE API.
- Populate your Home Assistant calendar with hourly events indicating electricity demand status (`Status`) in text and numerical form:
   ```
   "Status: ZALECANE UŻYTKOWANIE"  : 0
   "Status: NORMALNE UŻYTKOWANIE"  : 1
   "Status: ZALECANE OSZCZĘDZANIE" : 2
   "Status: WYMAGANE OGRANICZANIE" : 3
   ```

### Example Calendar Event

- **Title**: `Status: ZALECANE UŻYTKOWANIE`
- **Description**: `0`
- **Start Time**: `2026-10-30T00:00:00+01:00`
- **End Time**: `2026-10-30T01:00:00+01:00`

### Basic automation

You can create a template sensor helper using the following template to read the current or next event's status:
```
{{ state_attr('calendar.energetyczny_kompas', 'description') }}
```
The sensor state is the recommended usage status (in numerical form) for the active or next upcoming event.

### Advanced automation

The `calendar.get_events` action can query the hour starting one hour from now and store its status in `input_number.energetyczny_kompas_next_status` (a Number helper). If no event is returned, the helper is left unchanged.
```yaml
alias: Check Energetyczny Kompas next hour status
description: ""
triggers:
  - trigger: time_pattern
    minutes: /5
conditions: []
actions:
  - action: calendar.get_events
    metadata: {}
    data:
      start_date_time: "{{ now() + timedelta(hours=1) }}"
      duration:
        hours: 1
        minutes: 0
        seconds: 0
    target:
      entity_id: calendar.energetyczny_kompas
    response_variable: result
  - condition: template
    value_template: "{{ result['calendar.energetyczny_kompas'].events | count > 0 }}"
  - action: input_number.set_value
    metadata: {}
    data:
      value: "{{ result['calendar.energetyczny_kompas'].events[0].description }}"
    target:
      entity_id: input_number.energetyczny_kompas_next_status
mode: single
```
