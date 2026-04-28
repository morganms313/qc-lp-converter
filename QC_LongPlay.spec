# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for QC Long Play Converter
# Build:  pyinstaller QC_LongPlay.spec
# Output: dist/QC LongPlay Converter.app  (macOS)
#         dist/QC_LongPlay/QC_LongPlay.exe (Windows — zip the folder to distribute)

import sys
import os

# Bundle the tkdnd Tcl extension that tkinterdnd2 needs at runtime.
try:
    import tkinterdnd2 as _dnd
    _dnd_pkg_dir = os.path.dirname(_dnd.__file__)
    _dnd_datas = [(_dnd_pkg_dir, "tkinterdnd2")]
except ImportError:
    _dnd_datas = []

a = Analysis(
    ["gui.py"],
    pathex=[],
    binaries=[],
    datas=_dnd_datas,
    hiddenimports=[
        "tkinterdnd2",
        # openpyxl is not always auto-detected
        "openpyxl",
        "openpyxl.styles",
        "openpyxl.styles.fonts",
        "openpyxl.styles.fills",
        "openpyxl.styles.borders",
        "openpyxl.styles.alignment",
        "openpyxl.styles.numbers",
        "openpyxl.workbook",
        "openpyxl.workbook.child",
        "openpyxl.reader.excel",
        "openpyxl.writer.excel",
        "et_xmlfile",
        # pandas internals sometimes missed
        "pandas._libs.interval",
        "pandas._libs.tslibs.base",
        "pandas._libs.tslibs.np_datetime",
        "pandas._libs.tslibs.nattype",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "matplotlib",
        "scipy",
        "PIL",
        "IPython",
        "notebook",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,   # onedir: binaries collected separately
    name="QC_LongPlay",
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
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="QC_LongPlay",
)

# macOS: wrap the collected directory in a proper .app bundle
if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="QC LongPlay Converter.app",
        icon=None,           # replace with "icon.icns" if you have one
        bundle_identifier="com.qc.longplay.converter",
        info_plist={
            "NSHighResolutionCapable": True,
            "CFBundleShortVersionString": "1.0.0",
            "CFBundleName": "QC LongPlay Converter",
            "CFBundleDisplayName": "QC LongPlay Converter",
            "CFBundleDocumentTypes": [
                {
                    "CFBundleTypeName": "Excel Spreadsheet",
                    "CFBundleTypeExtensions": ["xlsx"],
                    "CFBundleTypeRole": "Viewer",
                }
            ],
        },
    )
