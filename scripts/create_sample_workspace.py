from __future__ import annotations

import argparse
import shutil
from decimal import Decimal

from chef_pricing.application.app_service import ChefPricingApp


def create_sample(path: str) -> ChefPricingApp:
    app = ChefPricingApp(path)
    tomato = app.save_ingredient(
        item_id=None, name="Tomato", category="Produce",
        purchase_unit="kg", purchase_quantity=Decimal("1"),
        purchase_price=Decimal("12"), waste_percent=Decimal("5"),
        supplier="Central Market", last_price_date="2026-06-12",
    )
    parmesan = app.save_ingredient(
        item_id=None, name="Parmesan", category="Dairy",
        purchase_unit="kg", purchase_quantity=Decimal("1"),
        purchase_price=Decimal("80"), waste_percent=Decimal("0"),
        supplier="Supplier A", last_price_date="2026-06-12",
    )
    mayo = app.save_ingredient(
        item_id=None, name="Mayonnaise", category="Sauces",
        purchase_unit="kg", purchase_quantity=Decimal("1"),
        purchase_price=Decimal("30"), waste_percent=Decimal("0"),
        supplier="Supplier B", last_price_date="2026-06-12",
    )
    sauce = app.save_preparation(
        item_id=None, name="House Sauce", category="Sauces",
        yield_quantity=Decimal("500"), yield_unit="g",
    )
    app.save_components("preparation", sauce.id, [
        {
            "component_type": "ingredient", "component_id": parmesan.id,
            "quantity": Decimal("80"), "unit": "g", "loss_percent": Decimal("0"),
        },
        {
            "component_type": "ingredient", "component_id": mayo.id,
            "quantity": Decimal("120"), "unit": "g", "loss_percent": Decimal("0"),
        },
    ])
    dish = app.save_dish(
        item_id=None, name="House Salad", category="Salads",
        serving_size=Decimal("1"), serving_unit="portion",
        food_cost=Decimal("30"), manual_price=Decimal("0"),
    )
    app.save_components("dish", dish.id, [
        {
            "component_type": "ingredient", "component_id": tomato.id,
            "quantity": Decimal("120"), "unit": "g", "loss_percent": Decimal("0"),
        },
        {
            "component_type": "preparation", "component_id": sauce.id,
            "quantity": Decimal("40"), "unit": "g", "loss_percent": Decimal("0"),
        },
    ])
    shutil.rmtree(app.workspace.backups_dir)
    app.workspace.backups_dir.mkdir()
    return app


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a demo workspace.")
    parser.add_argument("workspace")
    args = parser.parse_args()
    app = create_sample(args.workspace)
    print(f"Workspace created at {app.workspace.root}")
    print(f"Dishes: {len(app.repos.dishes.list_all())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
