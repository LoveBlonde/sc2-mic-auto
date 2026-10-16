$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
try {
    $pythonPath = $null
    foreach ($launcher in @('py', 'python')) {
        if (Get-Command $launcher -ErrorAction SilentlyContinue) {
            $candidate = if ($launcher -eq 'py') { & py -3 -c 'import sys; print(sys.executable)' 2>$null } else { & python -c 'import sys; print(sys.executable)' 2>$null }
            if ($LASTEXITCODE -eq 0 -and $candidate -and (Test-Path -LiteralPath $candidate)) { $pythonPath = $candidate; break }
        }
    }
    if (!$pythonPath) { throw 'Install Python 3.10+ from https://www.python.org/downloads/windows/ (enable Add Python to PATH), then run setup again.' }
    & $pythonPath -c 'import sys; assert sys.version_info >= (3,10), "Python 3.10+ required"'
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.10+ required.' }
    $pythonwPath = Join-Path (Split-Path $pythonPath) 'pythonw.exe'
    if (!(Test-Path -LiteralPath $pythonwPath)) { throw 'pythonw.exe is required. Install the standard Windows Python distribution.' }
    $startupLink = Join-Path ([Environment]::GetFolderPath('Startup')) 'SC2 Mic Auto.lnk'
    if ((Test-Path -LiteralPath $startupLink) -or (Test-Path -LiteralPath config.json)) {
        throw 'Existing configuration found. Run uninstall.cmd before reconfiguring.'
    }
    Write-Host 'Downloading SoundVolumeView from NirSoft (separate freeware license)...'
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $zip = Join-Path $PSScriptRoot 'soundvolumeview.zip'
    $tools = Join-Path $PSScriptRoot 'audio-tools'
    Invoke-WebRequest 'https://www.nirsoft.net/utils/soundvolumeview-x64.zip' -OutFile $zip -UseBasicParsing
    $expected = 'EE2C45553FB9FB31B71DB88B537C18E25C1A387A4A9009D081BDB38265C68E1F'
    if ((Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash -ne $expected) {
        throw 'SoundVolumeView download hash changed. No downloaded code was run. See README troubleshooting.'
    }
    Expand-Archive -LiteralPath $zip -DestinationPath $tools -Force
    Remove-Item -LiteralPath $zip
    $tool = Join-Path $tools 'SoundVolumeView.exe'
    $csv = Join-Path $PSScriptRoot 'devices.csv'
    Start-Process -FilePath $tool -ArgumentList @('/ShowDisabledDevices','1','/SaveFileEncoding','3','/scomma',('"' + $csv + '"')) -WindowStyle Hidden -Wait
    $devices = @(Import-Csv -LiteralPath $csv -Encoding UTF8 | Where-Object { $_.Type -eq 'Device' -and $_.Direction -eq 'Capture' })
    Remove-Item -LiteralPath $csv
    if (!$devices.Count) { throw 'No recording devices found. Connect your headset and retry.' }
    Write-Host "`nSelect the HEADSET MICROPHONE that fixes SC2 sound when disabled:"
    for ($i = 0; $i -lt $devices.Count; $i++) { Write-Host ("[{0}] {1} - {2} ({3})" -f ($i+1),$devices[$i].Name,$devices[$i].'Device Name',$devices[$i].'Device State') }
    $number = 0
    $answer = Read-Host 'Device number (or close this window to cancel)'
    if (![int]::TryParse($answer, [ref]$number) -or $number -lt 1 -or $number -gt $devices.Count) { throw 'Invalid selection.' }
    $device = $devices[$number-1]
    @{ device_id = $device.'Item ID'; device_name = $device.'Device Name' } | ConvertTo-Json | Set-Content -LiteralPath config.json -Encoding UTF8
    & $pythonPath (Join-Path $PSScriptRoot 'sc2_mic_auto.py') --check
    if ($LASTEXITCODE -ne 0) { throw 'Device configuration check failed.' }
    Remove-Item -LiteralPath sc2_mic_stop -ErrorAction SilentlyContinue
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($startupLink)
    $shortcut.TargetPath = $pythonwPath
    $shortcut.Arguments = '"' + (Join-Path $PSScriptRoot 'sc2_mic_auto.py') + '"'
    $shortcut.WorkingDirectory = $PSScriptRoot
    $shortcut.Description = 'Disable selected microphone while StarCraft II runs; restore on exit'
    $shortcut.Save()
    @{ python = $pythonPath; startup = $startupLink } | ConvertTo-Json | Set-Content -LiteralPath install.json -Encoding UTF8
    Start-Process -FilePath $pythonwPath -ArgumentList $shortcut.Arguments -WindowStyle Hidden
    Write-Host "`nInstalled. Launch SC2 normally. Keep this folder in its current location."
} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
    exit 1
}
