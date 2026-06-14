# -*- mode: python ; coding: utf-8 -*-
import re
from pathlib import Path

from PyInstaller.utils.win32.versioninfo import (
    FixedFileInfo,
    StringFileInfo,
    StringStruct,
    StringTable,
    VarFileInfo,
    VarStruct,
    VSVersionInfo,
)

root = Path(SPECPATH).parents[1]
version_source = (root / "src" / "chef_pricing" / "__init__.py").read_text(
    encoding="utf-8"
)
version = re.search(r'__version__\s*=\s*"([^"]+)"', version_source).group(1)
version_parts = tuple(int(part) for part in version.split(".")) + (0,)
version_parts = version_parts[:4]
version_info = VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=version_parts,
        prodvers=version_parts,
        mask=0x3F,
        flags=0x0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0),
    ),
    kids=[
        StringFileInfo([
            StringTable(
                "040904B0",
                [
                    StringStruct("CompanyName", "Lapidatto"),
                    StringStruct("FileDescription", "Chef Pricing"),
                    StringStruct("FileVersion", version),
                    StringStruct("InternalName", "ChefPricing"),
                    StringStruct("LegalCopyright", "Copyright Lapidatto"),
                    StringStruct("OriginalFilename", "ChefPricing.exe"),
                    StringStruct("ProductName", "Chef Pricing"),
                    StringStruct("ProductVersion", version),
                ],
            )
        ]),
        VarFileInfo([VarStruct("Translation", [1033, 1200])]),
    ],
)

a = Analysis(
    [str(root / "src" / "chef_pricing" / "main.py")],
    pathex=[str(root / "src")],
    binaries=[],
    datas=[
        (
            str(root / "src" / "chef_pricing" / "frontend" / "resources"),
            "chef_pricing/frontend/resources",
        ),
        (str(root / "data_templates"), "data_templates"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ChefPricing",
    version=version_info,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
coll = COLLECT(
    exe, a.binaries, a.datas, strip=False, upx=True, name="ChefPricing"
)
