# Chef Pricing

Offline desktop application for chefs and professional kitchens to calculate
recipe costs, food cost, suggested prices, and dish profit margins.

## Features

- ingredients with unit conversion, waste percentage, and price history;
- in-house preparations with recipes and cost per yield unit;
- dishes with technical recipe sheets, suggested prices, and manual prices;
- automatic cascading recalculation when an ingredient changes;
- relational CSV files editable in Excel and saved with UTF-8 BOM;
- schema, data type, relationship, and business rule validation;
- backups, restoration, and technical recipe sheet exports;
- PySide6 desktop interface and PyInstaller packaging.

## Running on Linux

Requires Python 3.12 or later.

The recommended setup creates an isolated virtual environment, installs the
dependencies, creates the demo workspace, and runs the tests:

```bash
chmod +x scripts/setup_linux.sh scripts/run_linux.sh
./scripts/setup_linux.sh
./scripts/run_linux.sh
```

The script also works on Debian/Ubuntu distributions where
`python3.12-venv` is not installed. In that case, it uses `virtualenv` in the
user directory without modifying the system Python packages.

Manual execution after setup:

```bash
source .venv/bin/activate
python -m chef_pricing.main --sample-workspace
```

To use a different workspace:

```bash
python -m chef_pricing.main --workspace "$HOME/Documents/ChefPricingData"
```

When started without arguments, the application displays the onboarding flow
on its first run and then reuses the most recently selected workspace.

### Graphics Troubleshooting

The application must be started within a Linux desktop session. Check:

```bash
echo "$DISPLAY"
echo "$WAYLAND_DISPLAY"
```

If an error related to the Qt Wayland plugin occurs, try:

```bash
QT_QPA_PLATFORM=xcb ./scripts/run_linux.sh
```

## Testing

```bash
source .venv/bin/activate
pytest -v
python scripts/create_sample_workspace.py ./ChefPricingDemo
python scripts/validate_workspace.py ./ChefPricingDemo
```

## Build Windows

On Windows 10/11 x64, install Python 3.12 x64 and Inno Setup 6. Then run:

```bat
scripts\build_windows_installer.bat
```

The installer will be generated at:

```text
dist\installer\ChefPricingSetup-0.1.0.exe
```

See [packaging/windows/installer_notes.md](packaging/windows/installer_notes.md)
for requirements, behavior details, and the release validation checklist.
