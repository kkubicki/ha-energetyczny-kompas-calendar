# Energetyczny Kompas Calendar
![Energetyczny Kompas logo](logo.png)

**Energetyczny Kompas Calendar** is a Home Assistant custom component that integrates data from [Energetyczny Kompas](https://www.energetycznykompas.pl). It fetches electricity demand and usage recommendations and displays them in your Home Assistant calendar.

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
- Fetch electricity demand data from [Energetyczny Kompas](https://www.energetycznykompas.pl).
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
- **Start Time**: `2024-12-20T00:00:00`
- **End Time**: `2024-12-20T00:59:59`

### Basic automation

You can create simple sensor helper using the following template:
```
{{ state_attr('calendar.energetyczny_kompas', 'description') }}
```
This will hold the recommended usage status (in numerical form) for the current hour.

### Advanced automation

For more advanced data manipulation, `calendar.get_event` action can be used. 
Here is example of checking next hour status and storing it in `input_number.energetyczny_kompas_next_status` (a `Number` type helper).
```
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
      duration:
        hours: 1
        minutes: 0
        seconds: 0
    target:
      entity_id: calendar.energetyczny_kompas
    response_variable: result
  - action: input_number.set_value
    metadata: {}
    data:
      value: "{{ result['calendar.energetyczny_kompas'].events[0].description }}"
    target:
      entity_id: input_number.energetyczny_kompas_next_status
mode: single
```





