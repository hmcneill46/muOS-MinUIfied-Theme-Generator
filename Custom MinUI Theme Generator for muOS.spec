# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['Custom MinUI Theme Generator for muOS.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('Font', 'Font'),
        ('Horizontal Logos', 'Horizontal Logos'),
        ('Overlays', 'Overlays'),
        ('Template Scheme', 'Template Scheme'),
        ('Theme Shell', 'Theme Shell'),
        ('_ConsoleAssociations.json', '.')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Custom MinUI Theme Generator for muOS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Custom MinUI Theme Generator for muOS'
)
