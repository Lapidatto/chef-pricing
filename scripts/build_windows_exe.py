from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]


def run(command: list[str], cwd: Path = ROOT) -> None:
    print("> " + " ".join(str(part) for part in command))
    subprocess.run(command, cwd=cwd, check=True)


def project_version() -> str:
    namespace: dict[str, str] = {}
    exec(
        (ROOT / "src" / "chef_pricing" / "__init__.py").read_text(
            encoding="utf-8"
        ),
        namespace,
    )
    return namespace["__version__"]


def find_inno_compiler() -> Path | None:
    configured = os.environ.get("INNO_SETUP_COMPILER")
    candidates = [
        Path(configured) if configured else None,
        Path(os.environ.get("ProgramFiles(x86)", "")) / "Inno Setup 6" / "ISCC.exe",
        Path(os.environ.get("ProgramFiles", "")) / "Inno Setup 6" / "ISCC.exe",
    ]
    command = shutil.which("ISCC.exe") or shutil.which("iscc")
    if command:
        candidates.insert(0, Path(command))
    return next((path for path in candidates if path and path.is_file()), None)


def main() -> int:
    if sys.platform != "win32":
        print("ERROR: the Windows installer must be built on Windows 10/11 x64.")
        return 1
    if sys.maxsize <= 2**32:
        print("ERROR: use 64-bit Python 3.12 to build the installer.")
        return 1
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print(
            "ERROR: PyInstaller was not found. Run: "
            "python -m pip install -r requirements-build.txt"
        )
        return 1
    inno = find_inno_compiler()
    if inno is None:
        print(
            "ERROR: Inno Setup 6 was not found. Install it or set "
            "INNO_SETUP_COMPILER to the full path of ISCC.exe."
        )
        return 1

    version = project_version()
    spec = ROOT / "packaging" / "pyinstaller" / "chef_pricing.spec"
    installer = ROOT / "packaging" / "windows" / "chef_pricing.iss"
    for directory in (ROOT / "build", ROOT / "dist"):
        if directory.exists():
            shutil.rmtree(directory)

    try:
        run([sys.executable, "-m", "pytest", "-v"])
        run([
            sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
            str(spec),
        ])
        executable = ROOT / "dist" / "ChefPricing" / "ChefPricing.exe"
        if not executable.is_file():
            raise RuntimeError(f"Executable was not generated: {executable}")
        run([str(executable), "--build-check"])
        run(
            [str(inno), f"/DMyAppVersion={version}", str(installer)],
            cwd=installer.parent,
        )
        output = ROOT / "dist" / "installer" / f"ChefPricingSetup-{version}.exe"
        if not output.is_file():
            raise RuntimeError(f"Installer was not generated: {output}")
    except (OSError, subprocess.CalledProcessError, RuntimeError) as exc:
        print(f"ERROR: build stopped: {exc}")
        return 1

    print(f"\nInstaller generated successfully:\n{output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
