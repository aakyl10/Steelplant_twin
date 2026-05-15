# Task 01 - Repo Hygiene

You are working on a final diploma practical project repository.

Goal: clean the repository for final practical submission without changing project logic.

Tasks:

1. Inspect the repository for accidental files, duplicate screenshot names, cache files, temporary outputs, and local-only artifacts.
2. Fix obvious filename issues such as duplicate extensions like `.png.png`.
3. Ensure `.gitignore` protects:
   - `.env`
   - `.venv/`
   - `venv/`
   - `__pycache__/`
   - `.pytest_cache/`
   - `.ruff_cache/`
   - Docker local volumes
   - IDE files
   - temporary outputs
4. Keep useful evidence screenshots, ML outputs, README, docs, tests, and source code.
5. Do not remove `data/processed/ml_dataset.csv` if it is intentionally used as an evidence artifact.
6. Do not change MQTT topic, InfluxDB bucket, measurement name, ports, SEC logic, ML feature list, or Docker service names.
7. Make minimal safe changes only.

After changes, the project must still support:

- `python -m pytest`
- `python -m ruff check .`
- `python -m ml.train_sec_regression`
- `docker compose up -d`
