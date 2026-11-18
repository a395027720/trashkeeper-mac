# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包配置（macOS）。

用法：pyinstaller --noconfirm --clean mac_main.spec --distpath dist/mac-release
"""

block_cipher = None

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[("./web", "web")],
    hiddenimports=[
        "api",
        "api.search",
        "api.trash",
        "conf.setting",
        "utilities.search",
        "utilities.trash",
        "utilities.log",
        "utilities.response",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy", "PIL"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="TrashKeeper",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = BUNDLE(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="废纸篓管家.app",
    icon="assets/icon.icns",
    bundle_identifier="com.gaojianqiang.trashkeeper",
)
