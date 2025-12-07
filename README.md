<div align="center" style="background-color: rgb(35, 35, 37);">
  <img src="images/banner.png" alt="MasjidBox Prayer Times Banner" width="100%">
</div>

# MasjidBox Prayer Times for Home Assistant
Accurate mosque-specific Adhan & Iqamah times directly from MasjidBox – ready for your dashboards and automations.

## Requirements

Before using this integration, you need:

1. Home Assistant – Any recent version of Home Assistant Core or OS
2. MasjidBox account / API key – From your MasjidBox administrator or dashboard
3. A MasjidBox mosque slug – For example: `bathgatemosque`
4. Internet access – The integration polls the MasjidBox cloud API

This is a custom component, not an official Home Assistant integration. It installs into `custom_components/masjidbox`.

## Why Use This?

Perfect for you if:

- You want authentic prayer times from your local mosque’s MasjidBox configuration
- You prefer integration with your mosque’s actual timetable, instead of generic calculated times
- You want clean Home Assistant entities (Fajr, Dhuhr, Asr, Maghrib, Isha, etc.) to:
  - Drive automations (lights, notifications, reminders)
  - Build dashboards and wall tablets
  - Integrate with other systems (voice, scenes, etc.)

Consider alternatives if:

- Your mosque does not use MasjidBox → Use a calculation-based prayer time integration
- You need offline calculations with no internet access
- You need global location-based calculations without depending on any mosque

Important: This integration reads from MasjidBox only. It does not create or modify any schedule on MasjidBox; it just mirrors the official timetable into Home Assistant.

## Key Features

- Mosque-sourced prayer times  
  Uses the same timetable your MasjidBox mosque publishes.

- Per-mosque configuration  
  Point it at any MasjidBox mosque via its slug and API key.

- Adhan & Iqamah entities  
  Timestamp sensors for:
  - Fajr, Sunrise, Dhuhr, Asr, Maghrib, Isha (Adhan)
  - Fajr, Dhuhr, Asr, Maghrib, Isha (Iqamah) – if configured

- Hijri date support  
  Text sensor with the formatted Hijri date for today.

- Config flow (UI setup)  
  Add and configure via Home Assistant UI – no YAML needed.

- DataUpdateCoordinator-based polling  
  Efficient, centralized polling of the MasjidBox API.

- Multiple mosques  
  Add more than one instance for different mosques (different slugs/API keys).

## What This Integration Provides

For each configured mosque, you get entities like:

- Adhan (call to prayer) times
  - `sensor.adhan_fajr`
  - `sensor.adhan_sunrise`
  - `sensor.adhan_dhuhr`
  - `sensor.adhan_asr`
  - `sensor.adhan_maghrib`
  - `sensor.adhan_isha`

- Iqamah (congregational) times (if MasjidBox provides them)
  - `sensor.iqamah_fajr`
  - `sensor.iqamah_dhuhr`
  - `sensor.iqamah_asr`
  - `sensor.iqamah_maghrib`
  - `sensor.iqamah_isha`

- Hijri calendar
  - `sensor.hijri_date` – e.g. “الجمعة 15 جمادى الآخرة 1447”

All Adhan/Iqamah sensors:

- Use `device_class: timestamp`
- Are real datetime values (UTC-aware)
- Are safe to use as triggers or conditions in automations

## Comparison With Alternatives

| Feature                        | MasjidBox Prayer Times                     | Generic Prayer Times Integrations  |
|--------------------------------|--------------------------------------------|------------------------------------|
| Source                         | MasjidBox mosque timetable (cloud)         | Local calculation (algorithms)     |
| Accuracy vs local mosque       | Matches mosque exactly                     | Often approximate                  |
| Requires mosque to use system  | Yes (MasjidBox)                            | No                                 |
| Config method                  | HA UI config flow                          | YAML or UI                         |
| Offline support                | No (needs internet)                        | Yes (once configured)              |
| Global coverage                | Only MasjidBox mosques                     | Any coordinates                    |

## Features

- Today-focused timetable  
  Always exposes today’s times from the `timetable[0]` entry returned by MasjidBox.

- Automatic daily window  
  Uses today’s midnight as the API `begin` parameter and fetches multiple days; entities are based on “day 0” (today).

- Time zone aware  
  API returns times in UTC (`Z`), converted safely for Home Assistant.

- Supports multiple mosques  
  Add separate instances for different MasjidBox slugs.

- Lightweight  
  One API call per interval (default hourly) via `DataUpdateCoordinator`.

- Debug-friendly logging  
  Optional verbose logging for easier troubleshooting.

## Quick Start

Say goodbye to manual prayer time updates. Get mosque-sourced times in 3 steps:

### 1. Install This Integration

Via HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=sohailpervaiz&repository=ha-masjidbox-custom-component&category=integration)

Or manually:

1. HACS → Integrations → ⋮ (menu) → Custom repositories  
2. Add: `https://github.com/sohailpervaiz/ha-masjidbox-custom-component`  
3. Category: Integration  
4. Install “MasjidBox Prayer Times”  
5. Restart Home Assistant

Manual Installation (for local dev or without HACS):

1. Download or clone this repository.
2. Copy `custom_components/masjidbox` into your Home Assistant `custom_components` folder, typically:  
   `/config/custom_components/masjidbox`
3. Restart Home Assistant.

### 2. Add the Integration via UI

1. Go to Settings → Devices & services → + Add Integration
2. Search for “MasjidBox Prayer Times”
3. Enter:
   - Mosque slug: for example `bathgatemosque`
   - MasjidBox API key
   - Days to fetch: for example `7` (default; only today is used for entities)
4. Click Submit and wait for success.

### 3. Use the Entities

After setup completes:

1. Go to Developer Tools → States
2. Look for entities such as:
   - `sensor.adhan_fajr`
   - `sensor.adhan_dhuhr`
   - `sensor.adhan_asr`
   - `sensor.adhan_maghrib`
   - `sensor.adhan_isha`
   - `sensor.iqamah_fajr`
   - `sensor.hijri_date`
3. Use them in:
   - Lovelace dashboards (entity cards, table cards)
   - Automations (for example, notify 10 minutes before Isha)
   - Scripts and templates (for example, showing next prayer time)

## Example Automations

### 1. Notify 10 Minutes Before Maghrib

automation:
  - alias: "Notify 10 minutes before Maghrib"
    trigger:
      - platform: template
        value_template: >
          {% set t = states('sensor.adhan_maghrib') | as_datetime %}
          {{ t is not none and
             now() >= (t - timedelta(minutes=10)) and
             now() < (t - timedelta(minutes=9)) }}
    action:
      - service: notify.mobile_app_your_phone
        data:
          message: "Maghrib is in 10 minutes."

### 2. Turn On Porch Light at Maghrib

NOTE: Depending on HA version, you may prefer a template trigger rather than a templated `at:` for time.

automation:
  - alias: "Turn on porch light at Maghrib"
    trigger:
      - platform: template
        value_template: >
          {% set t = states('sensor.adhan_maghrib') | as_datetime %}
          {{ t is not none and
             now().replace(second=0, microsecond=0) ==
             t.replace(second=0, microsecond=0) }}
    action:
      - service: light.turn_on
        target:
          entity_id: light.porch

## How It Works

### The Data Flow

1. Config Flow (UI)  
   You provide:
   - Mosque slug (for example `bathgatemosque`)
   - API key
   - Number of days to fetch

2. Coordinator Fetch  
   The integration’s DataUpdateCoordinator:

   - Computes `begin` = today at 00:00:00.000 UTC (`+00:00`)
   - Calls:

     https://api.masjidbox.com/1.0/masjidbox/landing/athany/{slug}?get=at&days={days}&begin={begin}

   - Uses header: apikey: <your_api_key>
   - Receives the JSON payload (including `timetable`)

3. Entity Update  
   Each sensor (Adhan/Iqamah/Hijri):

   - Reads from coordinator.data["timetable"][0]
   - Parses the relevant field (for example fajr, iqamah.fajr, hijri.formatted)
   - For times: converts "2025-12-05T06:09:00Z" into a timezone-aware datetime
   - Updates its native_value accordingly

4. Home Assistant UI / Automations  
   Home Assistant treats these as first-class entities:
   - They show up as timestamps or text
   - Can be used in triggers, conditions, and actions

### Example API-to-Entity Mapping

Given a timetable[0] entry like:

{
  "date": "2025-12-05T00:00:00Z",
  "fajr": "2025-12-05T06:09:00Z",
  "sunrise": "2025-12-05T08:28:00Z",
  "dhuhr": "2025-12-05T12:09:00Z",
  "asr": "2025-12-05T13:53:00Z",
  "maghrib": "2025-12-05T15:47:00Z",
  "isha": "2025-12-05T17:38:00Z",
  "hijri": {
    "formatted": "الجمعة 15 جمادى الآخرة 1447"
  },
  "iqamah": {
    "fajr": "2025-12-05T07:30:00Z",
    "dhuhr": "2025-12-05T13:15:00Z",
    "asr": "2025-12-05T14:00:00Z",
    "maghrib": "2025-12-05T15:47:00Z",
    "isha": "2025-12-05T19:00:00Z"
  }
}

This becomes:

- sensor.adhan_fajr → 2025-12-05T06:09:00+00:00
- sensor.iqamah_fajr → 2025-12-05T07:30:00+00:00
- sensor.adhan_maghrib → 2025-12-05T15:47:00+00:00
- sensor.iqamah_maghrib → 2025-12-05T15:47:00+00:00
- sensor.hijri_date → الجمعة 15 جمادى الآخرة 1447

## Debug Logging

Enable detailed logs in `configuration.yaml`:

logger:
  default: info
  logs:
    custom_components.masjidbox: debug

This will show:
- When the coordinator fetches data
- API URLs called (without the API key)
- Response status codes
- Any parsing or datetime conversion errors

## Troubleshooting

### Integration not showing in “Add Integration”

- Ensure files are in: `/config/custom_components/masjidbox/`
- Restart Home Assistant completely (not just reload YAML).
- Check logs for Python import errors.

### “Failed to fetch data from MasjidBox”

Possible causes:
- Invalid API key
- Wrong slug
- MasjidBox API is unavailable

Steps:
1. Check Logs → look for messages from `custom_components.masjidbox`.
2. Verify slug and API key with a direct curl command on your machine.
3. Try again after some time if the service is down.

### Sensors are `unknown` or `unavailable`

- Check if `timetable` is present in the API response.
- Confirm that at least one entry exists (`timetable[0]`).
- Look at debug logs for JSON structure issues.

### Time appears in UTC instead of local

- This is expected; Home Assistant will display in your local timezone in the UI.
- Internally, sensors keep UTC, which is correct for Home Assistant.

## Development & Contribution

If you are developing or extending this integration:

- Use a local dev environment (Docker or venv)
- Mount your `custom_components/masjidbox` folder directly into the HA container
- Restart Home Assistant after code changes

Pull requests and improvements are welcome:

- Additional sensors (for example `special.imsak`, `special.iftar`, Jumuah times)
- Exposing tomorrow’s times as separate entities
- Options flow for adjusting update intervals

## License

Add a license file (for example MIT). Example:

- MIT License – see `LICENSE` file for details.

## Acknowledgments

- Thanks to MasjidBox for providing a structured timetable API.
- Built on the Home Assistant custom integration framework.
- Inspired by the need for mosque-accurate prayer times in smart home automations.