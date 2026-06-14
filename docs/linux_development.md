# Local Development on Linux

## Automated Setup

```bash
chmod +x scripts/setup_linux.sh scripts/run_linux.sh
./scripts/setup_linux.sh
```

The setup:

1. checks Linux and Python 3.12+;
2. creates `.venv`;
3. uses `virtualenv` as a fallback when `python3-venv` is unavailable;
4. installs the project in editable mode;
5. creates `sample_workspace`;
6. runs the pytest suite.

## Open the Interface

```bash
./scripts/run_linux.sh
```

The shortcut opens `sample_workspace`, which already contains ingredients, an
in-house preparation, and a calculated dish.

To select another workspace:

```bash
source .venv/bin/activate
python -m chef_pricing.main --workspace /path/to/ChefPricingData
```

## Verification Commands

```bash
source .venv/bin/activate
python -m chef_pricing.main --help
pytest -v
python scripts/validate_workspace.py sample_workspace
```

## Graphics Dependencies

The official PySide6 wheels include Qt. The Linux distribution still needs the
basic graphics libraries and an X11 or Wayland session.

On Ubuntu/Debian, if Qt reports a missing system library:

```bash
sudo apt update
sudo apt install libegl1 libgl1 libxkbcommon-x11-0 libxcb-cursor0
```

To diagnose differences between Wayland and X11:

```bash
QT_DEBUG_PLUGINS=1 ./scripts/run_linux.sh
QT_QPA_PLATFORM=xcb ./scripts/run_linux.sh
```
