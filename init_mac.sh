#!/bin/sh

cd python_mac/install/bin/

echo creating virtual environment...
./python3.11 -m venv .venv

echo installing requirements...
".venv/bin/python3.11" -m pip install -r requirements.txt

echo set up complete!