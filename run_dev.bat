@echo off
echo ========================================
echo Starting DEV environment (Windows)
echo ========================================

set ENVIRONMENT=dev

echo.
echo [1/3] Starting PostgreSQL container...
docker-compose -f docker-compose.dev.yml up -d

echo.
echo [2/3] Waiting for database to be ready...
timeout /t 10 /nobreak

echo.
echo [3/3] Starting bot...
python main.py

pause
