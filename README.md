# Super Soco Custom

[![hacs][hacsbadge]][hacs] [![GitHub Release][releases-shield]][releases] [![GitHub Activity][commits-shield]][commits]

[![License][license-shield]][license] [![Project Maintenance][maintenance-shield]][user_profile]

Custom component for integrating your Super Soco or Vmoto Soco motorcycle into Home Assistant. It provides meaningful data like power status, battery percentage, location and a lot more.

![Example][img-example]

## Disclaimers

> This integration is based on the Super Soco & Vmoto Soco APIs, so it needs a combination of official ECU and active SIM contract that's currently working and sending data to Super Soco or Vmoto Soco servers. If this is not your case then sadly there's little to no chance that this integration will work for you. To put it simple: if your mobile app is not working, this won't work either.

> Please note that Super Soco & Vmoto Soco do not allow more than one client at a time, so any open session in the official app will be closed when using this integration (same as if you'd log in from a new device).

> This integration is not officially a part of Super Soco or Vmoto Soco. Additionally, this is NOT endorsed by Super Soco or Vmoto Soco in any way. Super Soco and Vmoto Soco are trademarks of Vmoto Limited.

## Installation

You can install this either using [HACS][hacs] (recommended way) or manually copying files:

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `super_soco_custom`.
4. Download _all_ the files from the `custom_components/super_soco_custom/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant

## Configuration

Configuration is done in the UI; go to "Configuration" -> "Integrations" click "+ Add Integration" and search for "Super Soco Custom", then enter your login credentials as you would do in the official app:

![Setup][img-setup]

You can configure some extra options by clicking on "Configure" once the integration is up and running:

![Config][img-config]

## Supported entities

- Power status and switch\*\*
- Battery percentage
- Estimated range
- ECU battery percentage
- Current speed
- Current location\* (device tracker)
- Current location via reverse geocoding\* (from [Open Street Map][openstreetmap], disabled by default)
- Current altitude (from [Open Topo Data][opentopodata])
- Current course in degrees
- Current course in 8-point wind rose
- Current distance from home\* with direction of travel (stationary/towards/away from/arrived)
- Current trip distance
- Current GSM signal strength\*
- Current GPS accuracy\*
- Last GPS fix time
- Last warning time\* with title and content
- Last trip time*, distance* and average speed\* (requires native tracking history to be enabled; updates every 10 minutes at most)
- Agreement (SIM card validity) start and end time\*\*
- Image URLs for both the vehicle and its logo\*\*
- Switches to enable/disable native tracking history and push notifications

_\* These entities include extra attributes with more details._
_\*\* These entities may not be available depending on native app support (Super Soco vs Vmoto Soco)._

## Known limitations

- Only one vehicle can be seen by this integration (I'm not lucky enough to own two Super Socos, so I don't know how would that look in the API responses)
- Vehicle diagnose can't be initiated from this integration, nor the resulting report be shown in HA
- Vehicle model seen by this integration may not match the actual model (the same issue happens in the official app if your ECU has been replaced with another one intended for a different model)
- ECU may always report a voltage level equal to zero (and hence zero battery percentage); the cause remains unknown

## Roadmap

- Increase test coverage
- Add altitude and reverse geocoding cache
- Allow speed threshold customization (this is used to filter out unwanted GPS noise when the vehicle is virtually still)
- Allow update interval customization while the vehicle is powered on (instead of forcing a 5 seconds interval)
- Add vehicle diagnosis for Vmoto Soco (Super Soco API doesn't support it)
- Add detailed battery information for Vmoto Soco (Super Soco API doesn't support it)

## Contributions are welcome!

If you want to contribute to this project please read the [Contribution guidelines](CONTRIBUTING.md)

## Special thanks

- Members of the [Super Soco - Spain][telegram] Telegram group who helped me testing this. Such nice and patient folks!
- [Home Assistant][homeassistant], [HACS][hacs], [Integration Blueprint][blueprint], [Open Street Map][openstreetmap], [Open Topo Data][opentopodata] and many more for providing the software and APIs this is built upon: "If I have seen further, it is by standing on the shoulders of Giants." - Isaac Newton

[blueprint]: https://github.com/custom-components/integration_blueprint
[commits-shield]: https://img.shields.io/github/commit-activity/y/drakhart/ha-super-soco-custom.svg?style=for-the-badge
[commits]: https://github.com/drakhart/ha-super-soco-custom/commits/main
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Default-orange?style=for-the-badge
[homeassistant]: https://www.home-assistant.io/
[img-config]: https://raw.githubusercontent.com/drakhart/ha-super-soco-custom/main/images/config.png
[img-example]: https://raw.githubusercontent.com/drakhart/ha-super-soco-custom/main/images/example.png
[img-setup]: https://raw.githubusercontent.com/drakhart/ha-super-soco-custom/main/images/setup.png
[license-shield]: https://img.shields.io/github/license/drakhart/ha-super-soco-custom.svg?style=for-the-badge
[license]: https://github.com/drakhart/ha-super-soco-custom/blob/main/LICENSE
[maintenance-shield]: https://img.shields.io/badge/maintainer-Brian%20Baidal%20%40drakhart-red.svg?style=for-the-badge
[openstreetmap]: https://www.openstreetmap.org/
[opentopodata]: https://www.opentopodata.org/
[releases-shield]: https://img.shields.io/github/v/release/drakhart/ha-super-soco-custom.svg?style=for-the-badge&color=yellowgreen&sort=semver&include_prereleases
[releases]: https://github.com/drakhart/ha-super-soco-custom/releases
[telegram]: https://t.me/supersocospain
[user_profile]: https://github.com/drakhart
