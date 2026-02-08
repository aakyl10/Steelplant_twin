import json
import math
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

from common import CONFIG


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class EAFSimulator:
    """Simple EAF-like simulator with phases (idle/melt/refine/downtime) and cumulative energy.

    This is NOT a physics model. It is an engineering-style signal generator:
    - realistic-ish ranges
    - repeatable scenarios
    - supports injected anomalies (optional)
    """

    MODES = ("idle", "melt", "refine", "downtime")

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.heat_id = 1
        self.mode = "idle"
        self.mode_t = 0
        self.energy_kwh_total = 0.0
        self.tons_current_heat = self._sample_tons()

        # anomaly switches (easy to show later)
        self.inject_idle_load_increase = False
        self.inject_sensor_bias = False
        self.sensor_bias_kw = 0.0

    def _sample_tons(self) -> float:
        return round(self.rng.uniform(80.0, 120.0), 1)

    def _advance_mode(self):
        # phase schedule per heat
        schedule = [
            ("idle", 60),
            ("melt", 240),
            ("refine", 180),
            ("downtime", 40),
        ]
        # find current
        idx = next((i for i, (m, _) in enumerate(schedule) if m == self.mode), 0)
        m, dur = schedule[idx]
        if self.mode_t >= dur:
            # next mode
            idx2 = (idx + 1) % len(schedule)
            self.mode, _ = schedule[idx2]
            self.mode_t = 0

            # new heat when coming back to idle from downtime
            if self.mode == "idle":
                self.heat_id += 1
                self.tons_current_heat = self._sample_tons()

    def step(self, dt_s: float = 1.0) -> dict:
        # update mode timing
        self.mode_t += dt_s
        self._advance_mode()

        # base power by mode (kW) with noise
        if self.mode == "idle":
            power_kw = self.rng.uniform(300, 600)
            if self.inject_idle_load_increase:
                power_kw *= 1.35  # anomaly: wasted idle power
        elif self.mode == "melt":
            power_kw = self.rng.uniform(2500, 4200)
        elif self.mode == "refine":
            power_kw = self.rng.uniform(1500, 2600)
        else:  # downtime
            power_kw = self.rng.uniform(100, 250)

        # add small oscillation + noise
        osc = 100 * math.sin(time.time() / 15.0)
        power_kw = max(0.0, power_kw + osc + self.rng.uniform(-50, 50))

        if self.inject_sensor_bias:
            power_kw += self.sensor_bias_kw  # anomaly: sensor offset

        # auxiliary loads
        pump_kw = self.rng.uniform(40, 120)
        compressor_kw = self.rng.uniform(30, 90)

        # integrate energy
        self.energy_kwh_total += (power_kw * dt_s) / 3600.0

        payload = {
            "ts": utc_now_iso(),
            "device_id": "eaf01_meter01",
            "heat_id": self.heat_id,
            "mode": self.mode,
            "power_kw": round(power_kw, 2),
            "energy_kwh_total": round(self.energy_kwh_total, 3),
            "pump_kw": round(pump_kw, 2),
            "compressor_kw": round(compressor_kw, 2),
            "tons": self.tons_current_heat,
        }
        return payload


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(CONFIG.mqtt_host, CONFIG.mqtt_port, keepalive=60)
    client.loop_start()

    sim = EAFSimulator(seed=42)

    print(f"Publishing to mqtt://{CONFIG.mqtt_host}:{CONFIG.mqtt_port} topic='{CONFIG.mqtt_topic}'")
    print("Press Ctrl+C to stop.")

    try:
        i = 0
        while True:
            msg = sim.step(dt_s=1.0)
            client.publish(CONFIG.mqtt_topic, json.dumps(msg), qos=0, retain=False)
            if i % 5 == 0:
                print(f"[PUB] {msg['ts']} heat={msg['heat_id']} mode={msg['mode']} power_kw={msg['power_kw']} energy={msg['energy_kwh_total']}")
            i += 1
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
