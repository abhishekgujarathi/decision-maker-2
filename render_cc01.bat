@echo off
setlocal EnableExtensions

set "ROOT=%~dp0"
set "BLENDER_EXE=F:\soft\BLENDER\blender.exe"

rem Project-specific Blender installation, including versioned subfolders.
if not exist "%BLENDER_EXE%" set "BLENDER_EXE="
if not defined BLENDER_EXE for /r "F:\soft\BLENDER" %%B in (blender.exe) do if not defined BLENDER_EXE set "BLENDER_EXE=%%~fB"

rem Prefer Blender available on PATH.
for /f "delims=" %%B in ('where blender.exe 2^>nul') do if not defined BLENDER_EXE set "BLENDER_EXE=%%B"

rem Fallback: common per-machine and per-user Blender install locations.
if not defined BLENDER_EXE for /d %%D in ("%ProgramFiles%\Blender Foundation\Blender *") do if exist "%%~D\blender.exe" set "BLENDER_EXE=%%~D\blender.exe"
if not defined BLENDER_EXE for /d %%D in ("%LOCALAPPDATA%\Programs\Blender Foundation\Blender *") do if exist "%%~D\blender.exe" set "BLENDER_EXE=%%~D\blender.exe"

if not defined BLENDER_EXE (
    echo Blender was not found.
    echo Add blender.exe to PATH or edit this file with its full path.
    pause
    exit /b 1
)

echo Using Blender: %BLENDER_EXE%
echo Rendering CC-01 review image...
"%BLENDER_EXE%" --background --python "%ROOT%render_cc01.py"
set "EXITCODE=%ERRORLEVEL%"

if "%EXITCODE%"=="0" echo Render complete. Check the newest numbered PNG in "%ROOT%outputs\full"
if not "%EXITCODE%"=="0" echo Render failed with exit code %EXITCODE%.
pause
exit /b %EXITCODE%
