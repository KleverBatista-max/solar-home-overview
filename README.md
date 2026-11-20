# Solar-aware home automation (Home Assistant + ESPHome)

A real, working home setup built to stop paying for electricity: solar panels + hybrid inverter + battery, with Home Assistant using the surplus solar energy to **pre-cool a room with the air conditioner during the day** so the battery isn't drained at night. Shared in case it helps someone in the community. *(Spanish speakers: los comentarios y nombres de las entidades están en español/inglés mezclados.)*

> Secrets (Wi‑Fi, API/OTA keys, network keys) are **not** included. Replace `!secret` values and regenerate ESPHome keys. Adapt IPs, entity IDs and device IDs to your own setup.

## What's inside
| Path | What |
|---|---|
| `esphome/solarinverter.yaml` + `esphome/components/modbus_sniffer/` | ESP32 + RS485 adapter that **passively listens to the inverter's Modbus bus** (custom component) and publishes SOC, battery V/A, loads, PV1/PV2, temperatures, grid, frequency |
| `esphome/airconditionermultisensor.yaml` | CT clamp on the A/C (power) + DS18B20 room temperature |
| `esphome/bedroomcontroller.yaml`, `yardcontroller.yaml` | Relay boards with physical switches |
| `esphome/archive/` | Earlier attempts (inverter, sniffer, Bluetti) |
| `homeassistant/configuration.yaml` | Template sensors: battery power, total solar, total load, a "real solar state" classifier (night → dawn → transition → firm solar), battery autonomy, kWh missing to target SOC, forecast-based "will it charge today", energy integrations |
| `homeassistant/automations.yaml` | **A/C SSC v5.8.4** solar controller (every 3 min), smart temperature stepping (26→20 °C), Bluetti charging with real surplus, router auto-reboot on internet loss, fridge water-pump guard, lights at sunrise/sunset |
| `homeassistant/storage/` | Helpers (`input_*`) and the **Broadlink RM mini 3 IR codes** for the A/C |
| `zigbee2mqtt/` | Zigbee2MQTT config (network key redacted) |
| `raspberry-original/` | First version: Python on a Raspberry Pi reading the inverter over Modbus RTU (9600 8N1) and sending IR codes — before moving the logic to Home Assistant |
| `docs/` | Inverter manual and the **Modbus register table (EN + original Chinese)** — hard to find outside China |
| `3d/` | Printable STL parts (cable holder, outlet and charger covers) |

## History
1. **Raspberry Pi + USB‑RS485 + Broadlink** — Python script, cron, rules based on surplus.
2. **ESP32 + ESPHome sniffer** — the inverter vendor's Modbus register table made it possible to read everything without disturbing the bus.
3. **Home Assistant** — all logic moved into automations with manual override, defensive dawn mode and sunset hand‑off.

Hardware: hybrid inverter (14.3 kWh battery), Broadlink RM mini 3, Echo Dot, Zigbee dongle, TP‑Link plugs, Bluetti AC70, Mosquitto.

## Notes
- Third‑party custom components used: HACS, Alexa Media Player, SmartIR, Bluetti BT (see `addons/`).
- Provided as‑is; verify every automation before running it against your own hardware.

## Author
Designed, built and programmed by [@KleverBatista-max](https://github.com/KleverBatista-max): the ESP32 firmware, the Modbus sniffer, the automations, the hardware choices and the 3D parts. Built with the help of AI assistants (ChatGPT, Claude) as tools.
