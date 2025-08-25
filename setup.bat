@echo off
REM OrcasAI Setup Script for Windows
REM This script sets up the virtual environment and installs dependencies

echo 🐋 Setting up OrcasAI Pod System...
echo ==================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Display Python version
echo ✅ Python version:
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created in ./venv/
) else (
    echo ✅ Virtual environment already exists in ./venv/
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

echo.
echo 🎉 Setup complete!
echo.
echo 📋 Next steps:
echo 1. Activate the virtual environment:
echo    venv\Scripts\activate
echo.
echo 2. Start using OrcasAI:
echo    python orcasai.py list
echo    python orcasai.py run content_creation --topic "Your topic here"
echo.
echo 🐋 Your orcas are ready to work together!
pause
