@echo off

cd python/install

echo creating virtual environment...
python.exe -m venv .venv

echo installing requirements...
".venv/Scripts/python.exe" -m pip install -r requirements.txt

echo set up complete!

pause