# ======================================================
# Financial Fraud Detection Dashboard - PowerShell Launcher
# ======================================================
# Right-click this file -> Run with PowerShell
# Or save and double-click RUN_DASHBOARD.ps1

# Get script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Try to find and activate Anaconda
$condaPaths = @(
    "$env:USERPROFILE\anaconda3",
    "$env:USERPROFILE\miniconda3",
    "C:\ProgramData\Anaconda3",
    "C:\ProgramData\Miniconda3"
)

foreach ($path in $condaPaths) {
    if (Test-Path "$path\Scripts\activate.ps1") {
        & "$path\Scripts\activate.ps1"
        Write-Host "✅ Conda activated" -ForegroundColor Green
        break
    }
}

# Launch Streamlit
Write-Host "🚀 Launching Fraud Detection Dashboard..." -ForegroundColor Cyan
Write-Host "📊 Opening in browser at http://localhost:8501" -ForegroundColor Yellow
Write-Host ""

python -m streamlit run app.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error: Could not launch dashboard" -ForegroundColor Red
    Write-Host "📝 Run this first: pip install -r requirements.txt" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
}
