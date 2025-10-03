# RollForge

Gestor de personajes para Dungeons & Dragons 5e con calculadora de tiradas.

## Características

- Interfaz moderna con tema oscuro
- Cálculo automático de modificadores D&D 5e
- Sistema de tarjetas con imágenes personalizables
- Guardado automático en JSON
- Importar/exportar personajes
- Generador de stats aleatorios (4d6 drop lowest)

## Instalación

**Windows (Instalador)**:

1. Descarga RollForge_Setup_v1.0.0.exe
2. Ejecuta el instalador
3. Lanza desde el menú inicio

## Uso Rápido

- **Nuevo personaje**: Click en "Nuevo Personaje"
- **Editar**: Click en "Editar" en la tarjeta
- **Eliminar**: Click en "Eliminar" en la tarjeta
- **Exportar/Importar**: Menú Archivo

## Desarrollo

### Por si no confías en el binario adjunto en el repo.

**Setup**:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Build**:

```powershell
.\build.ps1
```

**Crear Instalador**:

1. Instala [Inno Setup](https://jrsoftware.org/isdl.php)
2. Compila installer.iss (F9)

## Datos

Ubicación automática:

- **Windows**: %LOCALAPPDATA%\RollForge\data
- **Linux/Mac**: ~/.local/share/RollForge/data

## Stack

- Python 3.8+
- PySide6
- Pillow
- PyInstaller

## Licencia

MIT License - ver [LICENSE](LICENSE)

---

RollForge 2025
