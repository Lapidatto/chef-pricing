from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from chef_pricing import __version__
from chef_pricing.application.app_service import ChefPricingApp
from chef_pricing.frontend.app import run
from chef_pricing.product import PRODUCT_NAME, resource_path


def build_check() -> int:
    stylesheet = resource_path("frontend", "resources", "main.qss")
    if not stylesheet.is_file():
        print(f"ERROR: missing resource: {stylesheet}")
        return 1
    with tempfile.TemporaryDirectory(prefix="chef_pricing_build_check_") as directory:
        service = ChefPricingApp(directory)
        issues = service.validate()
        errors = [issue for issue in issues if issue.severity == "error"]
        if errors:
            print(f"ERROR: diagnostic workspace produced {len(errors)} error(s).")
            return 1
    print(f"{PRODUCT_NAME} {__version__}: bundle validated.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Chef Pricing - restaurant costing and pricing."
    )
    parser.add_argument(
        "--workspace",
        help="Workspace folder. If omitted, the last selected folder is used.",
    )
    parser.add_argument(
        "--sample-workspace",
        action="store_true",
        help="Open the demo workspace included with the project.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--build-check",
        action="store_true",
        help="Validate resources and a temporary workspace without opening the UI.",
    )
    args = parser.parse_args()
    if args.build_check:
        return build_check()
    workspace = args.workspace
    if args.sample_workspace:
        workspace = str(Path(__file__).parents[2] / "sample_workspace")
    return run(workspace)


if __name__ == "__main__":
    raise SystemExit(main())
