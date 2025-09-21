@echo off
py -3.12 -m pip install --upgrade pip
py -3.12 -m pip install -r requirements.txt
py -3.12 -m pip install pyinstaller
py -3.12 -m PyInstaller --noconfirm --onefile --windowed --name "BubulandiaTV" main.py
ECHO El ejecutable se encuentra en dist/BubulandiaTV.exe
