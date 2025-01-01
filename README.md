# Energetyczny Kompas

**Energetyczny Kompas** is a Home Assistant custom component that integrates data from [Energetyczny Kompas](https://www.energetycznykompas.pl). It fetches electricity demand and usage recommendations and displays them in your Home Assistant calendar.

## Installation

1. **Add to HACS**:
   - Open HACS in Home Assistant.
   - Go to "Integrations."
   - Click on the "+" button and add this repository (``https://github.com/kkubicki/ha-energetyczny-kompas-calendar) as a custom repository.

2. **Install the Integration**:
   - Search for "Energetyczny Kompas" in HACS and install it.

3. **Restart Home Assistant**:
   - Restart your Home Assistant to load the component.

4. **Configure**:
   - Add the integration via Home Assistant → Settings → Devices & Services → Add Integration → "Energetyczny Kompas."

## Usage

Once installed, this component will:
- Fetch electricity demand data from [Energetyczny Kompas](https://www.energetycznykompas.pl).
- Populate your Home Assistant calendar with hourly events indicating electricity demand (`Zapotrzebowanie`) and status (`Status`).

### Example Calendar Event

- **Title**: `Status: ZALECANE UŻYTKOWANIE`
- **Description**: `Zapotrzebowanie: 16163 MW`
- **Start Time**: `2024-12-20T00:00:00`
- **End Time**: `2024-12-20T00:59:59`

