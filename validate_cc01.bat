@echo off
setlocal EnableExtensions
set "ROOT=%~dp0"
set "BLENDER_EXE=F:\soft\BLENDER\blender.exe"
if not exist "%BLENDER_EXE%" set "BLENDER_EXE="
if not defined BLENDER_EXE for /r "F:\soft\BLENDER" %%B in (blender.exe) do if not defined BLENDER_EXE set "BLENDER_EXE=%%~fB"
if not defined BLENDER_EXE for /f "delims=" %%B in ('where blender.exe 2^>nul') do if not defined BLENDER_EXE set "BLENDER_EXE=%%B"
if not defined BLENDER_EXE (
    echo Blender was not found.
    echo Add blender.exe to PATH or edit this file with its full path.
    pause
    exit /b 1
)
echo Using Blender: %BLENDER_EXE%
echo Building CC-01 and running P0 validation...
"%BLENDER_EXE%" --background --python "%ROOT%validate_cc01.py"
set "EXITCODE=%ERRORLEVEL%"
if "%EXITCODE%"=="0" echo Validation passed. Report: "%ROOT%outputs\validation\phase1_validation.json"
if not "%EXITCODE%"=="0" echo Validation failed with exit code %EXITCODE%.
pause
exit /b %EXITCODE%
