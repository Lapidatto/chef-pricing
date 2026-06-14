from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from chef_pricing.domain.models import ValidationIssue
from chef_pricing.infrastructure.csv_storage import ENCODING, CsvWorkspace
from chef_pricing.infrastructure.schema import SCHEMAS


class WorkspaceValidator:
    def __init__(self, workspace: CsvWorkspace):
        self.workspace = workspace

    def validate(self) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        rows_by_key: dict[str, list[dict[str, str]]] = {}
        for key, schema in SCHEMAS.items():
            path = self.workspace.path_for(key)
            if not path.exists():
                issues.append(
                    ValidationIssue(
                        schema.filename, "error", "Required file is missing.",
                        suggestion="Recreate the file from Settings.",
                    )
                )
                continue
            try:
                with path.open("r", encoding=ENCODING, newline="") as handle:
                    reader = csv.DictReader(handle)
                    actual = tuple(reader.fieldnames or ())
                    missing = [field for field in schema.fields if field not in actual]
                    extra = [field for field in actual if field not in schema.fields]
                    for field in missing:
                        issues.append(
                            ValidationIssue(
                                schema.filename, "error",
                                f"Required column is missing: {field}.", field=field,
                                suggestion="Restore the original header.",
                            )
                        )
                    for field in extra:
                        issues.append(
                            ValidationIssue(
                                schema.filename, "warning",
                                f"Additional column will be ignored: {field}.", field=field,
                            )
                        )
                    if not missing:
                        rows_by_key[key] = list(reader)
            except (OSError, UnicodeError, csv.Error) as exc:
                issues.append(
                    ValidationIssue(schema.filename, "error", f"Read failure: {exc}")
                )

        for key, rows in rows_by_key.items():
            issues.extend(self._duplicates(key, rows))
            issues.extend(self._types(key, rows))
        issues.extend(self._relationships(rows_by_key))
        issues.extend(self._units(rows_by_key))
        issues.extend(self._business(rows_by_key))
        return issues

    @staticmethod
    def _duplicates(
        key: str, rows: list[dict[str, str]]
    ) -> list[ValidationIssue]:
        if key == "app_settings":
            id_field = "key"
        else:
            id_field = "id"
        filename = SCHEMAS[key].filename
        seen: set[str] = set()
        issues: list[ValidationIssue] = []
        for line, row in enumerate(rows, start=2):
            value = row.get(id_field, "").strip()
            if not value:
                issues.append(
                    ValidationIssue(
                        filename, "error", "Identifier is empty.", line, id_field
                    )
                )
            elif value in seen:
                issues.append(
                    ValidationIssue(
                        filename, "error", f"Duplicate identifier: {value}.",
                        line, id_field,
                    )
                )
            seen.add(value)
        return issues

    @staticmethod
    def _types(key: str, rows: list[dict[str, str]]) -> list[ValidationIssue]:
        numeric = {
            "ingredients": (
                "purchase_quantity", "purchase_price", "base_quantity",
                "cost_per_base_unit", "waste_percent",
            ),
            "preparations": (
                "yield_quantity", "total_cost", "cost_per_yield_unit",
            ),
            "preparation_components": ("quantity", "loss_percent"),
            "dishes": (
                "serving_size", "total_cost", "desired_food_cost_percent",
                "suggested_price", "manual_price", "profit_margin",
            ),
            "dish_components": ("quantity", "loss_percent"),
            "units": ("to_base_factor",),
            "price_history": ("purchase_quantity", "purchase_price"),
        }
        boolean_fields = {
            "ingredients": ("active",), "preparations": ("active",),
            "dishes": ("active",), "units": ("active",),
        }
        date_fields = {
            "ingredients": ("last_price_date",),
            "price_history": ("price_date",),
        }
        filename = SCHEMAS[key].filename
        issues: list[ValidationIssue] = []
        for line, row in enumerate(rows, start=2):
            for field in numeric.get(key, ()):
                try:
                    value = Decimal(row.get(field, ""))
                    if value < 0:
                        raise InvalidOperation
                    if "percent" in field and value >= 100:
                        raise InvalidOperation
                except (InvalidOperation, ValueError):
                    issues.append(
                        ValidationIssue(
                            filename, "error",
                            f'Invalid numeric value: "{row.get(field, "")}".',
                            line, field, "Enter a positive number using a decimal point.",
                        )
                    )
            for field in boolean_fields.get(key, ()):
                if row.get(field, "").lower() not in {"true", "false"}:
                    issues.append(
                        ValidationIssue(
                            filename, "error", "Use true or false.",
                            line, field, "Example: true",
                        )
                    )
            for field in date_fields.get(key, ()):
                value = row.get(field, "")
                if value:
                    try:
                        date.fromisoformat(value)
                    except ValueError:
                        issues.append(
                            ValidationIssue(
                                filename, "error", "Invalid date.",
                                line, field, "Use YYYY-MM-DD.",
                            )
                        )
        return issues

    @staticmethod
    def _relationships(
        rows: dict[str, list[dict[str, str]]]
    ) -> list[ValidationIssue]:
        ids = {
            key: {row.get("id", "") for row in rows.get(key, [])}
            for key in ("ingredients", "preparations", "dishes")
        }
        issues: list[ValidationIssue] = []
        relationships = (
            ("preparation_components", "preparation_id", "preparations"),
            ("dish_components", "dish_id", "dishes"),
            ("price_history", "ingredient_id", "ingredients"),
        )
        for source, field, target in relationships:
            for line, row in enumerate(rows.get(source, []), start=2):
                if row.get(field, "") not in ids[target]:
                    issues.append(
                        ValidationIssue(
                            SCHEMAS[source].filename, "error",
                            f"Reference not found: {row.get(field, '')}.",
                            line, field,
                        )
                    )
        for source in ("preparation_components", "dish_components"):
            for line, row in enumerate(rows.get(source, []), start=2):
                component_type = row.get("component_type", "")
                target = (
                    "ingredients" if component_type == "ingredient"
                    else "preparations" if component_type == "preparation"
                    else ""
                )
                if not target:
                    issues.append(
                        ValidationIssue(
                            SCHEMAS[source].filename, "error",
                            "Type must be ingredient or preparation.",
                            line, "component_type",
                        )
                    )
                elif row.get("component_id", "") not in ids[target]:
                    issues.append(
                        ValidationIssue(
                            SCHEMAS[source].filename, "error",
                            f"Component not found: {row.get('component_id', '')}.",
                            line, "component_id",
                        )
                    )
        return issues

    @staticmethod
    def _business(
        rows: dict[str, list[dict[str, str]]]
    ) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        inactive_ingredients = {
            row.get("id", "") for row in rows.get("ingredients", [])
            if row.get("active", "").lower() == "false"
        }
        inactive_preparations = {
            row.get("id", "") for row in rows.get("preparations", [])
            if row.get("active", "").lower() == "false"
        }
        for line, row in enumerate(rows.get("ingredients", []), start=2):
            try:
                if Decimal(row.get("purchase_price", "0")) <= 0:
                    issues.append(
                        ValidationIssue(
                            "ingredients.csv", "error",
                            "Ingredient has no purchase price.",
                            line, "purchase_price",
                            "Enter the latest purchase price.",
                        )
                    )
            except InvalidOperation:
                pass
        dish_components = {
            row.get("dish_id", "") for row in rows.get("dish_components", [])
        }
        preparation_components = {
            row.get("preparation_id", "")
            for row in rows.get("preparation_components", [])
        }
        for line, row in enumerate(rows.get("dishes", []), start=2):
            if row.get("id", "") not in dish_components:
                issues.append(
                    ValidationIssue(
                        "dishes.csv", "warning", "Dish has no components.",
                        line, "id", "Edit the dish recipe sheet.",
                    )
                )
            try:
                cost = Decimal(row.get("total_cost", "0"))
                manual = Decimal(row.get("manual_price", "0"))
                food_cost = Decimal(row.get("desired_food_cost_percent", "0"))
                if food_cost <= 0:
                    issues.append(
                        ValidationIssue(
                            "dishes.csv", "error",
                            "Food cost must be greater than zero.",
                            line, "desired_food_cost_percent",
                        )
                    )
                if manual > 0 and manual < cost:
                    issues.append(
                        ValidationIssue(
                            "dishes.csv", "warning",
                            "Manual price is below cost.",
                            line, "manual_price",
                        )
                    )
            except InvalidOperation:
                pass
        for line, row in enumerate(rows.get("preparations", []), start=2):
            if row.get("id", "") not in preparation_components:
                issues.append(
                    ValidationIssue(
                        "preparations.csv", "warning",
                        "Preparation has no components.", line, "id",
                    )
                )
            try:
                if Decimal(row.get("yield_quantity", "0")) <= 0:
                    issues.append(
                        ValidationIssue(
                            "preparations.csv", "error",
                            "Yield must be greater than zero.",
                            line, "yield_quantity",
                        )
                    )
            except InvalidOperation:
                pass
        for source in ("preparation_components", "dish_components"):
            filename = SCHEMAS[source].filename
            for line, row in enumerate(rows.get(source, []), start=2):
                component_id = row.get("component_id", "")
                component_type = row.get("component_type", "")
                inactive = (
                    component_type == "ingredient"
                    and component_id in inactive_ingredients
                ) or (
                    component_type == "preparation"
                    and component_id in inactive_preparations
                )
                if inactive:
                    issues.append(
                        ValidationIssue(
                            filename, "warning",
                            "An inactive component is used in an active recipe.",
                            line, "component_id",
                        )
                    )
                if (
                    source == "preparation_components"
                    and component_type == "preparation"
                ):
                    issues.append(
                        ValidationIssue(
                            filename, "error",
                            "Preparations cannot use other preparations in this version.",
                            line, "component_type",
                        )
                    )
        return issues

    @staticmethod
    def _units(
        rows: dict[str, list[dict[str, str]]]
    ) -> list[ValidationIssue]:
        units = {
            row.get("name", ""): row
            for row in rows.get("units", [])
            if row.get("active", "").lower() == "true"
        }
        ingredient_units = {
            row.get("id", ""): row.get("base_unit", "")
            for row in rows.get("ingredients", [])
        }
        preparation_units = {
            row.get("id", ""): row.get("yield_unit", "")
            for row in rows.get("preparations", [])
        }
        issues: list[ValidationIssue] = []
        for source in ("preparation_components", "dish_components"):
            filename = SCHEMAS[source].filename
            for line, row in enumerate(rows.get(source, []), start=2):
                used_unit = row.get("unit", "")
                component_type = row.get("component_type", "")
                target_unit = (
                    ingredient_units.get(row.get("component_id", ""), "")
                    if component_type == "ingredient"
                    else preparation_units.get(row.get("component_id", ""), "")
                )
                used = units.get(used_unit)
                target = units.get(target_unit)
                if not used:
                    issues.append(
                        ValidationIssue(
                            filename, "error", f"Unknown unit: {used_unit}.",
                            line, "unit",
                        )
                    )
                elif target and used.get("type") != target.get("type"):
                    issues.append(
                        ValidationIssue(
                            filename, "error",
                            f"Incompatible units: {used_unit} and {target_unit}.",
                            line, "unit",
                        )
                    )
        return issues

    @staticmethod
    def has_errors(issues: list[ValidationIssue]) -> bool:
        return any(issue.severity == "error" for issue in issues)
