@echo off
echo ========================================================
echo        ScamShield AI - Starting System Services
echo ========================================================

echo [1/2] Starting Flask Backend Server (Port 5000)...
start "ScamShield AI - Backend" cmd /k "cd backend && python run.py"

echo [2/2] Starting Vite React Frontend Dashboard (Port 5173)...
start "ScamShield AI - Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================================
echo   ScamShield AI is running!
echo   Dashboard:  http://localhost:5173
echo   Flask API:  http://127.0.0.1:5000
echo   Health:     http://127.0.0.1:5000/api/health
echo   Webhook:    http://127.0.0.1:5000/api/webhook/whatsapp
echo ========================================================
pause
