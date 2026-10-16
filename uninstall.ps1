$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
try {
    $link = Join-Path ([Environment]::GetFolderPath('Startup')) 'SC2 Mic Auto.lnk'
    if (Test-Path -LiteralPath $link) {
        $shell = New-Object -ComObject WScript.Shell
        $shortcut = $shell.CreateShortcut($link)
        if ($shortcut.WorkingDirectory -ne $PSScriptRoot) { throw 'The startup entry belongs to another installation. Uninstall that copy first.' }
        Remove-Item -LiteralPath $link
    }
    New-Item -ItemType File -Force -Path sc2_mic_stop | Out-Null
    Start-Sleep -Seconds 6
    if (Test-Path -LiteralPath sc2_mic_stop) {
        # No responsive watcher: do not race a potentially running process.
        throw 'Watcher did not acknowledge stop. Do not delete this folder yet. See README recovery instructions.'
    }
    if (Test-Path -LiteralPath sc2_mic_state.json) { throw 'Microphone restoration is pending. Reconnect the headset and see README recovery instructions.' }
    foreach ($file in @('config.json','install.json')) {
        if (Test-Path -LiteralPath $file) { Remove-Item -LiteralPath $file }
    }
    Write-Host 'Automatic startup removed, watcher stopped, original microphone state restored. You can delete this folder.'
} catch { Write-Host "ERROR: $_" -ForegroundColor Red; exit 1 }
