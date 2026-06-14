from __future__ import annotations

from pathlib import Path

PRODUCT_NAME = "Chef Pricing"
PUBLISHER = "Lapidatto"
EXECUTABLE_NAME = "ChefPricing.exe"
DEFAULT_WORKSPACE_NAME = "ChefPricingData"


def default_workspace_path(documents: str | Path | None = None) -> Path:
    documents = Path(documents) if documents else Path.home() / "Documents"
    return documents / DEFAULT_WORKSPACE_NAME


def resource_path(*parts: str) -> Path:
    """Return a bundled resource path in source and PyInstaller builds."""
    return Path(__file__).resolve().parent.joinpath(*parts)
