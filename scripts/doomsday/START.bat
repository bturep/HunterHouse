@echo off
rem Hunter House archive -- start the offline copy (Windows).
cd /d "%~dp0"
where py >nul 2>nul && (py -3 serve.py %* & goto :eof)
where python >nul 2>nul && (python serve.py %* & goto :eof)
echo Python 3 is not installed. Get it from https://www.python.org/downloads/ then run START.bat again.
pause
