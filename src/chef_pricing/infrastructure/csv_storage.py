from __future__ import annotations

import csv
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

from chef_pricing.domain.exceptions import NotFoundError
from chef_pricing.infrastructure.schema import DEFAULT_ROWS, SCHEMAS

ENCODING = "utf-8-sig"


def ensure_writable_directory(path: str | Path) -> Path:
    target = Path(path).expanduser()
    target.mkdir(parents=True, exist_ok=True)
    if not target.is_dir():
        raise OSError("The selected path is not a folder.")
    with tempfile.NamedTemporaryFile(
        dir=target, prefix=".chef_pricing_write_test_", delete=True
    ):
        pass
    return target.resolve()


class CsvWorkspace:
    def __init__(self, root: str | Path):
        self.root = Path(root).expanduser().resolve()
        self.data_dir = self.root / "data"
        self.backups_dir = self.root / "backups"
        self.exports_dir = self.root / "exports"

    def initialize(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        for key, schema in SCHEMAS.items():
            path = self.data_dir / schema.filename
            if not path.exists():
                write_rows(path, schema.fields, DEFAULT_ROWS.get(key, []))

    def path_for(self, key: str) -> Path:
        return self.data_dir / SCHEMAS[key].filename

    def read(self, key: str) -> list[dict[str, str]]:
        path = self.path_for(key)
        if not path.exists():
            raise NotFoundError(f"Missing file: {path.name}")
        with path.open("r", encoding=ENCODING, newline="") as handle:
            return list(csv.DictReader(handle))

    def write(self, key: str, rows: list[dict[str, str]]) -> None:
        schema = SCHEMAS[key]
        write_rows(self.path_for(key), schema.fields, rows)

    def settings(self) -> dict[str, str]:
        try:
            rows = self.read("app_settings")
        except NotFoundError:
            return {}
        return {row["key"]: row["value"] for row in rows}

    def update_setting(self, key: str, value: str) -> None:
        settings = self.settings()
        settings[key] = value
        self.write(
            "app_settings",
            [{"key": item, "value": setting} for item, setting in settings.items()],
        )

    def backup(self) -> Path | None:
        if not self.data_dir.exists():
            return None
        stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
        destination = self.backups_dir / stamp
        shutil.copytree(self.data_dir, destination)
        return destination

    def restore(self, backup_dir: str | Path) -> None:
        source = Path(backup_dir)
        if not source.is_dir():
            raise NotFoundError("Backup not found.")
        temporary = self.root / ".restore_tmp"
        if temporary.exists():
            shutil.rmtree(temporary)
        shutil.copytree(source, temporary)
        if self.data_dir.exists():
            shutil.rmtree(self.data_dir)
        temporary.replace(self.data_dir)

    def list_backups(self) -> list[Path]:
        if not self.backups_dir.exists():
            return []
        return sorted(
            (path for path in self.backups_dir.iterdir() if path.is_dir()),
            reverse=True,
        )


def write_rows(
    path: Path, fields: tuple[str, ...], rows: list[dict[str, str]]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(descriptor, "w", encoding=ENCODING, newline="") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n"
            )
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field, "") for field in fields})
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise
