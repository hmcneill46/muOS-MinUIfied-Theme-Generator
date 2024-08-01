# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Custom MinUI Theme Generator for muOS.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('Assets', 'Assets'),
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
    a.datas,
    [],
    name='minUIfied Theme Generator for muOS',
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
    icon=['Assets/Icons/macos.icns'],
)
app = BUNDLE(
    exe,
    name='minUIfied Theme Generator for muOS.app',
    icon='Assets/Icons/macos.icns',
    bundle_identifier=None,
)
