@echo off
echo ========================================
echo Installing Backend Dependencies
echo ========================================
echo.

echo Checking Python version...
python --version
echo.

echo Installing required packages...
pip install -r requirements.txt

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo You can now run the backend with:
echo   python main.py
echo.
pause
