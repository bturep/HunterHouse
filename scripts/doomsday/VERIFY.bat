@echo off
rem Hunter House archive -- check every file against the fixity manifest.
cd /d "%~dp0"
where py >nul 2>nul && (py -3 verify.py %* & goto :eof)
where python >nul 2>nul && (python verify.py %* & goto :eof)
echo Python 3 is not installed. Get it from https://www.python.org/downloads/
pause
