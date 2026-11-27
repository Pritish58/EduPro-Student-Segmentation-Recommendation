@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo        EduPro - Project Launcher
echo ==========================================

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    py -3 -m venv .venv
    if errorlevel 1 (
        echo Could not create virtual environment. Please install Python 3.10 or newer.
        pause
        exit /b 1
    )
)

echo Installing or checking project requirements...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto error
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto error

echo Starting EduPro dashboard...
".venv\Scripts\python.exe" -m streamlit run app.py
if errorlevel 1 goto error
goto end

:error
echo.
echo Something went wrong. Read the error shown above.
pause
exit /b 1

:end
pause
