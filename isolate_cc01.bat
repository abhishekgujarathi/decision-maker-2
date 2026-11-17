@echo off
setlocal EnableExtensions
set "ROOT=%~dp0"
set "BLENDER_EXE=F:\soft\BLENDER\blender.exe"
if not exist "%BLENDER_EXE%" set "BLENDER_EXE="
if not defined BLENDER_EXE for /r "F:\soft\BLENDER" %%B in (blender.exe) do if not defined BLENDER_EXE set "BLENDER_EXE=%%~fB"
if not defined BLENDER_EXE for /f "delims=" %%B in ('where blender.exe 2^>nul') do if not defined BLENDER_EXE set "BLENDER_EXE=%%B"
if not defined BLENDER_EXE (
    echo Blender was not found.
    pause
    exit /b 1
)
echo Using Blender: %BLENDER_EXE%
"%BLENDER_EXE%" --background --python "%ROOT%isolate_cc01.py" -- %*
set "EXITCODE=%ERRORLEVEL%"
if not "%EXITCODE%"=="0" echo Isolation command failed with exit code %EXITCODE%.
pause
exit /b %EXITCODE%
