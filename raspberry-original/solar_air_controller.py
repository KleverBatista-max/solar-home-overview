#!/usr/bin/env python3
import time
import datetime
import os
import sys
import subprocess
from collections import deque

import broadlink
from pymodbus.client import ModbusSerialClient
from ir_codes import AIR_OFF, AIR_22, AIR_24, AIR_26

# ================== LOCK PARA CRON ==================
LOCK_FILE = "/tmp/solar_air.lock"

if os.path.exists(LOCK_FILE):
    sys.exit(0)

with open(LOCK_FILE, "w") as f:
    f.write(str(os.getpid()))

def cleanup_and_exit():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
    sys.exit(0)

# ================== LOG EN VIVO (NO SD) ==================
def live(msg):
    subprocess.run(
        ["logger", "-t", "solar-air", msg],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

# ================= CONFIG MODBUS =================
MODBUS_PORT = "/dev/ttyUSB0"

client = ModbusSerialClient(
    port=MODBUS_PORT,
    baudrate=9600,
    parity="N",
    stopbits=1,
    bytesize=8,
    timeout=1
)

if not client.connect():
    live("❌ No se pudo conectar al inversor")
    cleanup_and_exit()

live("🔌 Modbus conectado")

def read_reg(addr, signed=False, scale=1):
    try:
        r = client.read_holding_registers(addr, count=1)
        if not r or not hasattr(r, "registers"):
            return None
        v = r.registers[0]
        if signed and v > 32767:
            v -= 65536
        return v * scale
    except Exception:
        return None

# ================= CONFIG GENERAL =================
SOC_TARGET = 82
SOC_MIN = 20

START_TIME  = datetime.time(9, 50)
TARGET_TIME = datetime.time(14, 0)

READ_INTERVAL = 2
AVG_WINDOW = 30

SOLAR_MARGIN = 300
BATT_DISCHARGE_A = 0.8  # A positivos = usando batería

# ================= BROADLINK =================
devices = broadlink.discover(timeout=5)
if not devices:
    live("❌ No se encontró Broadlink")
    cleanup_and_exit()

device = devices[0]
device.auth()

last_sent = None

def send_ir(code, label, info):
    global last_sent
    if last_sent != label:
        device.send_data(code)
        last_sent = label
        live(f"AIR → {label} | {info}")

# ================= BUFFERS =================
buf_solar = deque(maxlen=AVG_WINDOW)
buf_house = deque(maxlen=AVG_WINDOW)
buf_batti = deque(maxlen=AVG_WINDOW)

last_good_soc = None

live("🚀 Control solar + aire iniciado")

# ================= LOOP PRINCIPAL =================
try:
    while True:
        soc_raw = read_reg(0x100)
        battI   = read_reg(0x102, signed=True, scale=0.1) or 0
        mppt1   = read_reg(0x10E) or 0
        mppt2   = read_reg(0x10F) or 0
        solar   = mppt1 + mppt2
        casa    = abs(read_reg(0x21B) or 0) + abs(read_reg(0x232) or 0)

        if soc_raw is not None and 0 <= soc_raw <= 100:
            soc = soc_raw
            last_good_soc = soc_raw
        else:
            soc = last_good_soc

        if soc is None:
            time.sleep(READ_INTERVAL)
            continue

        buf_solar.append(solar)
        buf_house.append(casa)
        buf_batti.append(battI)

        solar_avg = sum(buf_solar) / len(buf_solar)
        house_avg = sum(buf_house) / len(buf_house)
        batt_avg  = sum(buf_batti) / len(buf_batti)

        excedente = solar_avg - house_avg
        now = datetime.datetime.now().time()

        using_battery = batt_avg > BATT_DISCHARGE_A
        label = None

        if now < START_TIME:
            label = None
        elif soc <= SOC_MIN:
            label = "OFF"
        elif using_battery:
            label = "OFF"
        else:
            if now < TARGET_TIME and soc < SOC_TARGET:
                label = "26" if excedente > 1200 else "OFF"
            else:
                if excedente > 1200:
                    label = "22"
                elif excedente > 700:
                    label = "24"
                elif excedente > 300:
                    label = "26"
                else:
                    label = "OFF"

        info = (
            f"SOC {soc}% | Solar {int(solar_avg)}W | "
            f"Casa {int(house_avg)}W | Batt {batt_avg:.1f}A | "
            f"Ex {int(excedente)}W"
        )

        if label == "OFF":
            send_ir(AIR_OFF, "OFF", info)
        elif label == "22":
            send_ir(AIR_22, "22", info)
        elif label == "24":
            send_ir(AIR_24, "24", info)
        elif label == "26":
            send_ir(AIR_26, "26", info)

        time.sleep(READ_INTERVAL)

except KeyboardInterrupt:
    live("👋 Saliendo")
    cleanup_and_exit()
