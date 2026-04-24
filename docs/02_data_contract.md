# Data Contract

## Purpose

This document defines the required telemetry structure for the virtual compressed-air plant.

The same data contract must be used by:

- telemetry generator;
- MQTT payload;
- InfluxDB storage;
- dataset export;
- ML training pipeline.

The goal is to keep the IoT and ML parts consistent.

---

## Expected dataset size

The simulation must generate:

```text
30 days * 24 hours * 12 intervals per hour = 8640 rows