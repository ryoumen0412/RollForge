# Script de PowerShell para construir el ejecutable
# Uso: .\build.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RollForge - Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Detectar Python del venv
$pythonExe = ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    Write-Host "ERROR: No se encuentra el entorno virtual en .venv\" -ForegroundColor Red
    Write-Host "Ejecuta primero: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

# 1. Verificar que PyInstaller esté instalado
Write-Host "1. Verificando PyInstaller en venv..." -ForegroundColor Yellow
try {
    & $pythonExe -m PyInstaller --version | Out-Null
    Write-Host "   OK PyInstaller encontrado" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "   ERROR PyInstaller no encontrado. Instalando en venv..." -ForegroundColor Red
    & $pythonExe -m pip install pyinstaller
    Write-Host ""
}

# 2. Convertir ícono PNG a ICO
Write-Host "2. Convirtiendo icono PNG a ICO..." -ForegroundColor Yellow
if (Test-Path "assets\dragon.png") {
    & $pythonExe convert_icon.py
    Write-Host ""
} else {
    Write-Host "   ADVERTENCIA: No se encuentra assets\dragon.png" -ForegroundColor Yellow
    Write-Host ""
}

# 3. Limpiar builds anteriores
Write-Host "3. Limpiando builds anteriores..." -ForegroundColor Yellow
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
    Write-Host "   OK Carpeta dist eliminada" -ForegroundColor Green
}
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
    Write-Host "   OK Carpeta build eliminada" -ForegroundColor Green
}
# NO eliminar .spec - lo necesitamos para el build
Write-Host ""

# 4. Construir ejecutable
Write-Host "4. Construyendo ejecutable con PyInstaller..." -ForegroundColor Yellow
Write-Host "   Usando spec file con todas las dependencias del venv" -ForegroundColor Gray
Write-Host "   Esto puede tomar varios minutos..." -ForegroundColor Gray
Write-Host ""

# Usar el archivo .spec que tiene todas las dependencias configuradas
if (Test-Path "RollForge.spec") {
    & $pythonExe -m PyInstaller --clean --noconfirm RollForge.spec
} else {
    Write-Host "   ERROR: No se encuentra RollForge.spec" -ForegroundColor Red
    exit 1
}

# 5. Verificar resultado
Write-Host ""
Write-Host "5. Verificando resultado..." -ForegroundColor Yellow
if (Test-Path "dist\RollForge\RollForge.exe") {
    $fileSize = (Get-Item "dist\RollForge\RollForge.exe").Length / 1MB
    $fileSizeRounded = [math]::Round($fileSize, 2)
    Write-Host "   OK Ejecutable creado exitosamente!" -ForegroundColor Green
    Write-Host "   Ubicacion: dist\RollForge\RollForge.exe" -ForegroundColor Green
    Write-Host "   Tamano: $fileSizeRounded MB" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  BUILD COMPLETADO!" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Siguiente paso: Crear instalador con Inno Setup" -ForegroundColor Yellow
    Write-Host "Ver instrucciones en: build_installer.md" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "   ERROR: No se pudo crear el ejecutable" -ForegroundColor Red
    Write-Host "   Revisa los errores anteriores" -ForegroundColor Red
    Write-Host ""
    exit 1
}
