Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "          CAREER AI: INTELLIGENT AGENT" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# Check for npm
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] npm is not installed. Please install Node.js." -ForegroundColor Red
    pause
    exit
}

# Check for python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] python is not installed. Please install Python." -ForegroundColor Red
    pause
    exit
}

Write-Host "[1/2] Starting Frontend (port 5173)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "[2/2] Starting Backend (port 8000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-ExecutionPolicy", "Bypass", "-NoExit", "-Command", "cd backend; .\venv\Scripts\Activate.ps1; uvicorn main:app --reload --reload-exclude '*.sqlite', '*.sqlite-journal', 'uploads/*' --port 8000"

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host " Both services are starting."
Write-Host " - Frontend: http://localhost:5173"
Write-Host " - Backend: http://localhost:8000/docs"
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit this launcher window (services will keep running)"
