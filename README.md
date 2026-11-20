# Solar home overview

A house that stopped paying for electricity: solar panels, a hybrid inverter and a battery, with ESP32s, Home Assistant and a lot of small automations around them. This repo is only the **map**; each project lives in its own repo and they call each other through Home Assistant entities.

```
 inverter ──(Modbus)──▶ ESP32 sniffer ──▶ Home Assistant sensors
                                              │
                    ┌─────────────────────────┼───────────────────────┐
                    ▼                         ▼                       ▼
            solar A/C controller      Bluetti charger        (your own consumers)
            (pre-cools with surplus)  (stores surplus)

 house relay controllers  ── independent: lights, relays, fridge pump guard, router reboot
```

| Project | What it does | Depends on |
|---|---|---|
| [solar-inverter-modbus-monitor](https://github.com/KleverBatista-max/solar-inverter-modbus-monitor) | Passive Modbus sniffer on ESP32 + sensors + inverter docs (EN/ZH) | — |
| [solar-ac-controller](https://github.com/KleverBatista-max/solar-ac-controller) | Pre-cools a room with the A/C on solar surplus (Broadlink IR) | inverter monitor |
| [bluetti-solar-charger](https://github.com/KleverBatista-max/bluetti-solar-charger) | Charges a Bluetti AC70 only with real surplus | inverter monitor |
| [house-relay-controllers](https://github.com/KleverBatista-max/house-relay-controllers) | Relay boards, Zigbee2MQTT, lights, pump guard, router reboot | — |
| [piezas-3d](https://github.com/KleverBatista-max/piezas-3d) | 3D-printable parts I designed (not Home Assistant) | — |

## Story
1. **Raspberry Pi + USB‑RS485 + Broadlink:** a Python script reads the inverter and sends IR codes to the A/C.
2. **ESP32 + ESPHome:** the inverter supplier shared the Modbus register table (Chinese), which allowed a passive sniffer.
3. **Home Assistant:** the logic moved into automations with manual override, dawn mode and sunset hand‑off.
4. **Forecast:** Forecast.Solar (location, weather and panel orientation) tells the controller how much sun is still coming today, so it only pre-cools when the sun will pay for it.
5. **Off‑site backups:** encrypted daily backups to the cloud, because "just in case it all blows up".

More of the story (and the chat history behind it) will be added as it is recovered.

Created by **John Batista** ([@KleverBatista-max](https://github.com/KleverBatista-max)). Built with AI assistants (ChatGPT, Claude) as tools. MIT licensed.
