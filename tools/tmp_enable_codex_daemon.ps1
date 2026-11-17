# Run this file from PowerShell opened with "Run as administrator".
# Adds narrow process exclusions for the Codex daemon and helper executables.

$bin = "$env:APPDATA\nvm\v22.22.2\node_modules\@openai\codex\node_modules\@openai\codex-win32-x64\vendor\x86_64-pc-windows-msvc\bin"
$blenderPath = 'F:\soft\BLENDER'

if (Test-Path -LiteralPath $blenderPath) {
    Add-MpPreference -ExclusionPath $blenderPath
    Write-Host "Added Defender path exclusion: $blenderPath"
} else {
    Write-Warning "Blender path is not accessible from this PowerShell session: $blenderPath"
}

$processes = @(
    "$bin\codex.exe",
    "$bin\codex-command-runner.exe",
    "$bin\codex-code-mode-host.exe",
    "$bin\codex-windows-sandbox-setup.exe"
)

foreach ($process in $processes) {
    if (Test-Path -LiteralPath $process) {
        Add-MpPreference -ExclusionProcess $process
        Write-Host "Added Defender process exclusion: $process"
    } else {
        Write-Warning "Executable not found: $process"
    }
}

Write-Host "`nCurrent Codex-related process exclusions:"
Get-MpPreference |
    Select-Object -ExpandProperty ExclusionProcess |
    Where-Object { $_ -match 'codex' }

Write-Host "`nRestart Codex normally afterward; do not use --no-daemon."
