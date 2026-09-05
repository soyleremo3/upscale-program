# Downloads the Real-ESRGAN ncnn-vulkan engine (binary + bundled models)
# into tools/realesrgan-ncnn-vulkan/. The engine is gitignored, so every
# fresh clone needs to run this once.

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$toolsDir = Join-Path $root "tools"
$engineDir = Join-Path $toolsDir "realesrgan-ncnn-vulkan"
$zipPath = Join-Path $toolsDir "realesrgan-ncnn-vulkan-windows.zip"
$url = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-windows.zip"

if (Test-Path (Join-Path $engineDir "realesrgan-ncnn-vulkan.exe")) {
    Write-Host "Engine already present at $engineDir"
    exit 0
}

New-Item -ItemType Directory -Force -Path $toolsDir | Out-Null

Write-Host "Downloading engine from $url ..."
Invoke-WebRequest -Uri $url -OutFile $zipPath

Write-Host "Scanning download with Windows Defender ..."
Start-MpScan -ScanType CustomScan -ScanPath $zipPath

$extractDir = Join-Path $toolsDir "_extract_tmp"
if (Test-Path $extractDir) { Remove-Item -Recurse -Force $extractDir }
Expand-Archive -Path $zipPath -DestinationPath $extractDir -Force

New-Item -ItemType Directory -Force -Path $engineDir | Out-Null
Move-Item (Join-Path $extractDir "realesrgan-ncnn-vulkan.exe") $engineDir
Move-Item (Join-Path $extractDir "vcomp140.dll") $engineDir
Move-Item (Join-Path $extractDir "vcomp140d.dll") $engineDir
Move-Item (Join-Path $extractDir "models") $engineDir

Remove-Item -Recurse -Force $extractDir
Remove-Item -Force $zipPath

Write-Host "Engine ready at $engineDir"
