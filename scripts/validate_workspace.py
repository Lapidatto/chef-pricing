from __future__ import annotations

import argparse

from chef_pricing.application.app_service import ChefPricingApp


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Chef Pricing workspace.")
    parser.add_argument("workspace")
    args = parser.parse_args()
    issues = ChefPricingApp(args.workspace).validate()
    if not issues:
        print("Workspace is valid.")
        return 0
    for issue in issues:
        location = f"{issue.file}:{issue.line or '-'}"
        print(f"[{issue.severity.upper()}] {location} {issue.field} {issue.message}")
    return 1 if any(issue.severity == "error" for issue in issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())
