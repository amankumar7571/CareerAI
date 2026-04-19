@echo off
setlocal
title CareerAI Launcher

echo ===================================================
echo           CAREER AI: INTELLIGENT AGENT
echo ===================================================
echo.

:: Check for Node.js
where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] npm is not installed. Please install Node.js.
    pause
    exit /b
)

:: Check for Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] python is not installed. Please install Python.
    pause
    exit /b
)

echo [1/2] Starting Frontend (port 5173)...
start "CareerAI-Frontend" cmd /c "cd frontend && npm run dev"

echo [2/2] Starting Backend (port 8000)...
start "CareerAI-Backend" cmd /c "cd backend && call venv\Scripts\activate.bat && uvicorn main:app --reload --reload-exclude *.sqlite --reload-exclude *.sqlite-journal --reload-exclude uploads/* --port 8000"

echo.
echo ===================================================
echo  Both services are starting. 
echo  - Frontend: http://localhost:5173
echo  - Backend: http://localhost:8000/docs
echo ===================================================
echo.
pause
