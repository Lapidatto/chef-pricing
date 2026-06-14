from decimal import Decimal

from chef_pricing.application.app_service import ChefPricingApp


def test_complete_ingredient_preparation_dish_workflow(tmp_path):
    app = ChefPricingApp(tmp_path)
    parmesan = app.save_ingredient(
        item_id=None, name="Parmesan", category="Dairy",
        purchase_unit="kg", purchase_quantity=Decimal("1"),
        purchase_price=Decimal("80"), waste_percent=Decimal("0"),
    )
    mayo = app.save_ingredient(
        item_id=None, name="Mayonnaise", category="Sauces",
        purchase_unit="kg", purchase_quantity=Decimal("1"),
        purchase_price=Decimal("30"), waste_percent=Decimal("0"),
    )
    sauce = app.save_preparation(
        item_id=None, name="Caesar Dressing", category="Sauces",
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
    sauce = app.repos.preparations.get(sauce.id)
    assert sauce.total_cost == Decimal("10")
    assert sauce.cost_per_yield_unit == Decimal("0.02")

    dish = app.save_dish(
        item_id=None, name="Caesar Salad", category="Salads",
        serving_size=Decimal("1"), serving_unit="portion",
        food_cost=Decimal("30"), manual_price=Decimal("0"),
    )
    app.save_components("dish", dish.id, [
        {
            "component_type": "preparation", "component_id": sauce.id,
            "quantity": Decimal("40"), "unit": "g", "loss_percent": Decimal("0"),
        },
        {
            "component_type": "ingredient", "component_id": parmesan.id,
            "quantity": Decimal("15"), "unit": "g", "loss_percent": Decimal("0"),
        },
    ])
    dish = app.repos.dishes.get(dish.id)
    assert dish.total_cost == Decimal("2.00")
    assert dish.suggested_price == Decimal("6.67")
    assert dish.profit_margin.quantize(Decimal("0.01")) == Decimal("70.01")
    report = app.export_dishes()
    recipe_sheet = app.export_dish_sheet(dish.id)
    assert report.name == "priced_dishes.csv"
    assert recipe_sheet.name == "technical_sheet_caesar_salad.csv"
    assert report.read_text(encoding="utf-8-sig").splitlines()[0] == (
        "id,name,category,total_cost,food_cost_percent,suggested_price,"
        "manual_price,profit_margin"
    )
    assert recipe_sheet.read_text(encoding="utf-8-sig").splitlines()[0] == (
        "type,component,quantity,unit,waste_percent,cost"
    )


def test_price_change_recalculates_dependents(tmp_path):
    app = ChefPricingApp(tmp_path)
    ingredient = app.save_ingredient(
        item_id=None, name="Tomato", category="Produce",
        purchase_unit="kg", purchase_quantity=Decimal("1"),
        purchase_price=Decimal("10"), waste_percent=Decimal("0"),
    )
    dish = app.save_dish(
        item_id=None, name="Roasted Tomato", category="Starter",
        serving_size=Decimal("1"), serving_unit="portion",
        food_cost=Decimal("25"), manual_price=Decimal("0"),
    )
    app.save_components("dish", dish.id, [{
        "component_type": "ingredient", "component_id": ingredient.id,
        "quantity": Decimal("100"), "unit": "g", "loss_percent": Decimal("0"),
    }])
    assert app.repos.dishes.get(dish.id).total_cost == Decimal("1.00")
    app.save_ingredient(
        item_id=ingredient.id, name=ingredient.name, category=ingredient.category,
        purchase_unit="kg", purchase_quantity=Decimal("1"),
        purchase_price=Decimal("20"), waste_percent=Decimal("0"),
    )
    assert app.repos.dishes.get(dish.id).total_cost == Decimal("2.00")
    assert len(app.repos.price_history.list_all()) == 2
