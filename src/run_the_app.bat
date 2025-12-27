@echo off
cd /d "%~dp0"
echo Activating virtual environment...
call .\venv\Scripts\activate
echo Starting AuraControl...
python gui_main.py
pause
