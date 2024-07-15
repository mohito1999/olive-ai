#!/usr/bin/env bash

export PYTHONPATH=".:app:$PYTHONPATH"

cd /app
. venv/bin/activate

python main.py

