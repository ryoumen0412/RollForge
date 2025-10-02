# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('data', 'data'),
        ('dnd_dm_app', 'dnd_dm_app'),
    ],
    hiddenimports=[
        'dnd_dm_app',
        'dnd_dm_app.gui',
        'dnd_dm_app.gui.main_window',
        'dnd_dm_app.gui.character_card',
        'dnd_dm_app.gui.character_grid',
        'dnd_dm_app.gui.character_form',
        'dnd_dm_app.gui.dice_roll_widget',
        'dnd_dm_app.models',
        'dnd_dm_app.models.character',
        'dnd_dm_app.models.dnd_classes',
        'dnd_dm_app.models.dnd_system',
        'dnd_dm_app.utils',
        'dnd_dm_app.utils.data_manager',
        'dnd_dm_app.utils.image_utils',
        'dnd_dm_app.utils.theme',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'tkinter',
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RollForge',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets\\dragon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RollForge',
)
