@echo off
REM Usage: convert_longplay.bat "C:\path\to\QC_Report.xlsx"
set SCRIPT_DIR=%~dp0
set PY=%SCRIPT_DIR%qc_longplay_convert.py

if "%~1"=="" (
  echo Usage: convert_longplay.bat "C:\path\to\QC_Report.xlsx"
  exit /b 1
)

python "%PY%" "%~1"
