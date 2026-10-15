#!/bin/sh
set -e
python src/01_extract_dongjak.py
python src/02_deficit_analysis.py
python src/03_simulation.py
python src/04_regression.py
