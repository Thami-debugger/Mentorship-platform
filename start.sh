#!/usr/bin/env bash
set -e

python -m pip install -r requirements.txt --target ./vendor
export PYTHONPATH=./vendor
python run.py
