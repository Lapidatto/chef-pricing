from __future__ import annotations

import csv
from dataclasses import replace
from datetime import date
from decimal import Decimal
from pathlib import Path

from chef_pricing.application.services import (
    PricingService,
    RecipeCostService,
    UnitConversionService,
)
from chef_pricing.application.validation import WorkspaceValidator
from chef_pricing.domain.exceptions import ValidationError
from chef_pricing.domain.models import (
    Dish,
    Ingredient,
    Preparation,
    PriceHistory,
    RecipeComponent,
    ValidationIssue,
    decimal_text,
)
from chef_pricing.infrastructure.csv_storage import ENCODING, CsvWorkspace
from chef_pricing.infrastructure.repositories import Repositories


class ChefPricingApp:
    def __init__(self, workspace_path: str | Path):
        self.workspace = CsvWorkspace(workspace_path)
        if not self.workspace.data_dir.exists():
            self.workspace.initialize()
        self.repos = Repositories(self.workspace)

    def conversion(self) -> UnitConversionService:
        return UnitConversionService(self.repos.units.list_all())

    def next_id(self, prefix: str, existing: list[str]) -> str:
        numbers = []
        for value in existing:
            if value.startswith(f"{prefix}_"):
                try:
                    numbers.append(int(value.rsplit("_", 1)[1]))
                except ValueError:
                    continue
        return f"{prefix}_{max(numbers, default=0) + 1:03d}"

    def validate(self) -> list[ValidationIssue]:
        return WorkspaceValidator(self.workspace).validate()

    def dashboard(self) -> dict[str, object]:
        ingredients = self.repos.ingredients.list_all()
        preparations = self.repos.preparations.list_all()
        dishes = self.repos.dishes.list_all()
        issues = self.validate()
        history = sorted(
            self.repos.price_history.list_all(),
            key=lambda item: item.price_date,
            reverse=True,
        )[:5]
        return {
            "ingredients": len([item for item in ingredients if item.active]),
            "preparations": len([item for item in preparations if item.active]),
            "dishes": len([item for item in dishes if item.active]),
            "dishes_without_price": len(
                [item for item in dishes if item.active and item.suggested_price <= 0]
            ),
            "ingredients_without_price": len(
                [item for item in ingredients if item.active and item.purchase_price <= 0]
            ),
            "issues": issues,
            "history": history,
        }

    def save_ingredient(
        self,
        *,
        item_id: str | None,
        name: str,
        category: str,
        purchase_unit: str,
        purchase_quantity: Decimal,
        purchase_price: Decimal,
        waste_percent: Decimal,
        supplier: str = "",
        last_price_date: str = "",
        notes: str = "",
        active: bool = True,
    ) -> Ingredient:
        if not name.strip():
            raise ValidationError("Enter the ingredient name.")
        if waste_percent < 0 or waste_percent >= 100:
            raise ValidationError("Waste must be between 0 and 99.99%.")
        base_unit, base_quantity, unit_cost = PricingService.ingredient_base_values(
            purchase_quantity, purchase_price, purchase_unit, self.conversion()
        )
        ingredients = self.repos.ingredients.list_all()
        old = self.repos.ingredients.get(item_id) if item_id else None
        identifier = item_id or self.next_id(
            "ing", [item.id for item in ingredients]
        )
        item = Ingredient(
            id=identifier, name=name.strip(), category=category.strip(),
            purchase_unit=purchase_unit, purchase_quantity=purchase_quantity,
            purchase_price=purchase_price, base_unit=base_unit,
            base_quantity=base_quantity, cost_per_base_unit=unit_cost,
            waste_percent=waste_percent, supplier=supplier.strip(),
            last_price_date=last_price_date or date.today().isoformat(),
            active=active, notes=notes.strip(),
        )
        self.workspace.backup()
        if old:
            self.repos.ingredients.update(item)
        else:
            self.repos.ingredients.save(item)
        if old is None or (
            old.purchase_price != purchase_price
            or old.purchase_quantity != purchase_quantity
            or old.purchase_unit != purchase_unit
        ):
            history = self.repos.price_history.list_all()
            self.repos.price_history.save(
                PriceHistory(
                    id=self.next_id("ph", [entry.id for entry in history]),
                    ingredient_id=item.id, purchase_unit=purchase_unit,
                    purchase_quantity=purchase_quantity,
                    purchase_price=purchase_price, supplier=supplier.strip(),
                    price_date=item.last_price_date, notes="Updated by the application",
                )
            )
            self.recalculate_all()
        return item

    def save_preparation(
        self,
        *,
        item_id: str | None,
        name: str,
        category: str,
        yield_quantity: Decimal,
        yield_unit: str,
        notes: str = "",
        active: bool = True,
    ) -> Preparation:
        if not name.strip():
            raise ValidationError("Enter the preparation name.")
        if yield_quantity <= 0:
            raise ValidationError("Yield must be greater than zero.")
        preparations = self.repos.preparations.list_all()
        old = self.repos.preparations.get(item_id) if item_id else None
        item = Preparation(
            id=item_id or self.next_id(
                "prep", [entry.id for entry in preparations]
            ),
            name=name.strip(), category=category.strip(),
            yield_quantity=yield_quantity, yield_unit=yield_unit,
            total_cost=old.total_cost if old else Decimal("0"),
            cost_per_yield_unit=old.cost_per_yield_unit if old else Decimal("0"),
            active=active, notes=notes.strip(),
        )
        self.workspace.backup()
        if old:
            self.repos.preparations.update(item)
        else:
            self.repos.preparations.save(item)
        self.recalculate_preparation(item.id)
        return self.repos.preparations.get(item.id)

    def save_dish(
        self,
        *,
        item_id: str | None,
        name: str,
        category: str,
        serving_size: Decimal,
        serving_unit: str,
        food_cost: Decimal,
        manual_price: Decimal,
        notes: str = "",
        active: bool = True,
    ) -> Dish:
        if not name.strip():
            raise ValidationError("Enter the dish name.")
        if serving_size <= 0:
            raise ValidationError("Serving size must be greater than zero.")
        if food_cost <= 0 or food_cost > 100:
            raise ValidationError("Food cost must be between 0 and 100%.")
        dishes = self.repos.dishes.list_all()
        old = self.repos.dishes.get(item_id) if item_id else None
        item = Dish(
            id=item_id or self.next_id("dish", [entry.id for entry in dishes]),
            name=name.strip(), category=category.strip(),
            serving_size=serving_size, serving_unit=serving_unit,
            total_cost=old.total_cost if old else Decimal("0"),
            desired_food_cost_percent=food_cost,
            suggested_price=old.suggested_price if old else Decimal("0"),
            manual_price=manual_price,
            profit_margin=old.profit_margin if old else Decimal("0"),
            active=active, notes=notes.strip(),
        )
        self.workspace.backup()
        if old:
            self.repos.dishes.update(item)
        else:
            self.repos.dishes.save(item)
        self.recalculate_dish(item.id)
        return self.repos.dishes.get(item.id)

    def save_components(
        self, parent_type: str, parent_id: str, components: list[dict[str, object]]
    ) -> None:
        repository = (
            self.repos.preparation_components
            if parent_type == "preparation"
            else self.repos.dish_components
        )
        existing_ids = [item.id for item in repository.list_all()]
        prefix = "pc" if parent_type == "preparation" else "dc"
        models: list[RecipeComponent] = []
        for raw in components:
            component_type = str(raw["component_type"])
            if parent_type == "preparation" and component_type != "ingredient":
                raise ValidationError(
                    "In this version, in-house preparations may only use ingredients."
                )
            model_id = str(raw.get("id") or self.next_id(prefix, existing_ids))
            existing_ids.append(model_id)
            quantity = Decimal(str(raw["quantity"]))
            loss = Decimal(str(raw.get("loss_percent", "0")))
            if quantity <= 0:
                raise ValidationError("Component quantity must be greater than zero.")
            models.append(
                RecipeComponent(
                    id=model_id, parent_id=parent_id,
                    component_type=component_type,
                    component_id=str(raw["component_id"]),
                    quantity=quantity, unit=str(raw["unit"]),
                    loss_percent=loss, notes=str(raw.get("notes", "")),
                )
            )
        self.workspace.backup()
        repository.replace_for(parent_id, models)
        if parent_type == "preparation":
            self.recalculate_preparation(parent_id)
            self.recalculate_all_dishes()
        else:
            self.recalculate_dish(parent_id)

    def _cost_service(self) -> RecipeCostService:
        return RecipeCostService(
            {item.id: item for item in self.repos.ingredients.list_all()},
            {item.id: item for item in self.repos.preparations.list_all()},
            self.conversion(),
        )

    def recalculate_preparation(self, item_id: str) -> Preparation:
        item = self.repos.preparations.get(item_id)
        components = self.repos.preparation_components.list_for(item_id)
        total = self._cost_service().total(components)
        unit_cost = total / item.yield_quantity if item.yield_quantity > 0 else Decimal("0")
        updated = replace(
            item, total_cost=total, cost_per_yield_unit=unit_cost
        )
        return self.repos.preparations.update(updated)

    def recalculate_dish(self, item_id: str) -> Dish:
        item = self.repos.dishes.get(item_id)
        components = self.repos.dish_components.list_for(item_id)
        total = self._cost_service().total(components)
        raw_suggested = PricingService.suggested_price(
            total, item.desired_food_cost_percent
        )
        strategy = self.workspace.settings().get("commercial_rounding", "none")
        suggested = PricingService.commercial_round(raw_suggested, strategy)
        sale_price = item.manual_price if item.manual_price > 0 else suggested
        updated = replace(
            item, total_cost=total, suggested_price=suggested,
            profit_margin=PricingService.profit_margin(total, sale_price),
        )
        return self.repos.dishes.update(updated)

    def recalculate_all_dishes(self) -> None:
        for item in self.repos.dishes.list_all():
            self.recalculate_dish(item.id)

    def recalculate_all(self) -> None:
        for item in self.repos.preparations.list_all():
            self.recalculate_preparation(item.id)
        self.recalculate_all_dishes()

    def component_options(
        self, parent_type: str
    ) -> list[tuple[str, str, str, str]]:
        options = [
            ("ingredient", item.id, item.name, item.base_unit)
            for item in self.repos.ingredients.list_all() if item.active
        ]
        if parent_type == "dish":
            options.extend(
                ("preparation", item.id, item.name, item.yield_unit)
                for item in self.repos.preparations.list_all() if item.active
            )
        return options

    def export_dishes(self) -> Path:
        path = self.workspace.exports_dir / "priced_dishes.csv"
        fields = (
            "id", "name", "category", "total_cost", "food_cost_percent",
            "suggested_price", "manual_price", "profit_margin",
        )
        with path.open("w", encoding=ENCODING, newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for item in self.repos.dishes.list_all():
                writer.writerow({
                    "id": item.id, "name": item.name, "category": item.category,
                    "total_cost": decimal_text(item.total_cost),
                    "food_cost_percent": decimal_text(item.desired_food_cost_percent),
                    "suggested_price": decimal_text(item.suggested_price),
                    "manual_price": decimal_text(item.manual_price),
                    "profit_margin": decimal_text(item.profit_margin),
                })
        return path

    def export_dish_sheet(self, dish_id: str) -> Path:
        dish = self.repos.dishes.get(dish_id)
        components = self.repos.dish_components.list_for(dish_id)
        ingredients = {item.id: item for item in self.repos.ingredients.list_all()}
        preparations = {
            item.id: item for item in self.repos.preparations.list_all()
        }
        cost_service = self._cost_service()
        safe_name = "".join(
            char.lower() if char.isalnum() else "_" for char in dish.name
        ).strip("_")
        path = self.workspace.exports_dir / f"technical_sheet_{safe_name}.csv"
        fields = (
            "type", "component", "quantity", "unit", "waste_percent", "cost"
        )
        with path.open("w", encoding=ENCODING, newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for component in components:
                source = (
                    ingredients if component.component_type == "ingredient"
                    else preparations
                )
                writer.writerow({
                    "type": component.component_type,
                    "component": source[component.component_id].name,
                    "quantity": decimal_text(component.quantity),
                    "unit": component.unit,
                    "waste_percent": decimal_text(component.loss_percent),
                    "cost": decimal_text(cost_service.component_cost(component)),
                })
            writer.writerow({
                "type": "TOTAL", "component": dish.name,
                "quantity": "", "unit": "", "waste_percent": "",
                "cost": decimal_text(dish.total_cost),
            })
        return path
