#!/usr/bin/env bash
# Rebuild every output and figure from the raw Big Data Bowl data. Run from the repo root.
set -e
mkdir -p output figures
python3 scripts/01_build_targets.py
python3 scripts/02_build_separation.py
python3 scripts/03_build_sticks.py
python3 scripts/04_fig_3rd_down_sticks.py
python3 scripts/05_fig_checkdown.py
python3 scripts/06_fig_open_vs_value.py
