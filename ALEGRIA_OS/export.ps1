# ALEGRIA OS - Script de Exportación Limpia
$SourcePath = ".\"
$ExportName = "ALEGRIA_OS_Export_$(Get-Date -Format 'yyyyMMdd_HHmm').zip"
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$DestinationPath = Join-Path $DesktopPath $ExportName

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Empezando empaquetado de ALEGRIA OS..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Directorios temporales para armar el empaquetado sin mugre
$TempDir = Join-Path $env:TEMP "AlegriaOS_Export"
If (Test-Path $TempDir) { Remove-Item $TempDir -Recurse -Force }
New-Item -ItemType Directory -Path $TempDir | Out-Null

Write-Host "[1/3] Copiando archivos (excluyendo entornos, módulos y duplicados)..."

# Definimos exactamente qué NO Copiar para hacer el export super liviano
$Exclude = @(
    "node_modules",
    "venv",
    "__pycache__",
    ".git",
    "alegria_sdk",
    "dist",
    "build",
    "Desktop",
    "*.zip",
    "*.log"
)

# Copiar al Temp (Omitiendo la basura que pesa GBs)
Get-ChildItem -Path $SourcePath -Exclude $Exclude | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination $TempDir -Recurse -Force
}

# Quitar el directorio alegria_sdk de la raiz, pero asegurar que backend/src/alegria_sdk exista
$RootSDK = Join-Path $TempDir "alegria_sdk"
if (Test-Path $RootSDK) {
    Remove-Item $RootSDK -Recurse -Force
}

Write-Host "[2/3] Comprimiendo el OS..."
Compress-Archive -Path "$TempDir\*" -DestinationPath $DestinationPath -Force

Write-Host "[3/3] Limpiando archivos temporales..."
Remove-Item $TempDir -Recurse -Force

Write-Host ""
Write-Host "✅ ¡Exportación Exitosa!" -ForegroundColor Green
Write-Host "El archivo listo para entregar está en tu ESCRITORIO:" -ForegroundColor Yellow
Write-Host "$DestinationPath" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Cyan
