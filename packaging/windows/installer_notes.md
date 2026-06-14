# Windows Installer

## Build Machine Requirements

- 64-bit Windows 10 or 11;
- Python 3.12 x64 with Python Launcher (`py`);
- Inno Setup 6;
- access to PowerShell or Command Prompt.

The build must run on Windows. PyInstaller does not cross-compile from Linux to
Windows.

## Build the Installer

From the project root:

```bat
scripts\build_windows_installer.bat
```

The script:

1. creates `.venv-windows`;
2. installs the project dependencies, test tools, and PyInstaller;
3. runs the pytest suite;
4. cleans `build` and `dist`;
5. generates `dist\ChefPricing\ChefPricing.exe`;
6. runs the `--build-check` diagnostic;
7. compiles the installer with Inno Setup.

Output:

```text
dist\installer\ChefPricingSetup-0.1.0.exe
```

If Inno Setup is installed in a non-standard location:

```bat
set INNO_SETUP_COMPILER=C:\Tools\Inno Setup 6\ISCC.exe
scripts\build_windows_installer.bat
```

## Installation Behavior

- installs per user in `%LocalAppData%\Programs\Chef Pricing`;
- does not request administrator privileges during the normal flow;
- creates a Start menu shortcut;
- offers a desktop shortcut;
- offers to launch the application on the Finish page;
- registers an uninstaller under Installed Apps;
- never installs or removes CSV files inside the application folder.

The workspace is selected on the first launch and remains separate from the
installation. Updates and uninstallations preserve `data`, `backups`, and
`exports`.

## Release Validation Checklist

- test the executable in `dist\ChefPricing` before the installer;
- install on a clean Windows machine without Python;
- test folders with spaces and accents, as well as another drive;
- open CSV files in Excel and confirm UTF-8 with BOM;
- update over a previous installation;
- uninstall and verify that the workspace remains;
- repeat on Windows 10 and Windows 11 x64.

This version is not digitally signed. SmartScreen may display
“Unknown publisher”.
