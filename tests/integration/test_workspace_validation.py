from pathlib import Path

from chef_pricing.application.app_service import ChefPricingApp
from chef_pricing.infrastructure.csv_storage import ensure_writable_directory


def test_new_workspace_is_valid(tmp_path):
    app = ChefPricingApp(tmp_path)
    assert app.validate() == []


def test_existing_workspace_files_are_not_overwritten(tmp_path):
    app = ChefPricingApp(tmp_path)
    ingredients = app.workspace.path_for("ingredients")
    original = ingredients.read_bytes()
    ChefPricingApp(tmp_path)
    assert ingredients.read_bytes() == original


def test_workspace_supports_spaces_and_accents(tmp_path):
    workspace = tmp_path / "Café Kitchen Data"
    app = ChefPricingApp(workspace)
    assert app.workspace.data_dir.is_dir()
    assert app.validate() == []


def test_workspace_write_probe_creates_and_validates_directory(tmp_path):
    workspace = tmp_path / "Other Drive" / "Chef Pricing"
    assert ensure_writable_directory(workspace) == workspace.resolve()
    assert list(workspace.glob(".chef_pricing_write_test_*")) == []


def test_invalid_excel_edit_is_reported(tmp_path):
    app = ChefPricingApp(tmp_path)
    path = app.workspace.path_for("ingredients")
    path.write_text(
        "id,name,category,purchase_unit,purchase_quantity,purchase_price,"
        "base_unit,base_quantity,cost_per_base_unit,waste_percent,supplier,"
        "last_price_date,active,notes\n"
        "ing_001,Tomato,Produce,kg,1,abc,g,1000,0.01,0,,2026-06-12,true,\n",
        encoding="utf-8-sig",
    )
    issues = app.validate()
    assert any(
        issue.file == "ingredients.csv"
        and issue.field == "purchase_price"
        and issue.severity == "error"
        for issue in issues
    )


def test_missing_file_is_reported_and_recreated(tmp_path):
    app = ChefPricingApp(tmp_path)
    path = app.workspace.path_for("dishes")
    Path(path).unlink()
    restarted = ChefPricingApp(tmp_path)
    assert any(issue.file == "dishes.csv" for issue in restarted.validate())
    assert restarted.repos.dishes.list_all() == []
    app.workspace.initialize()
    assert path.exists()


def test_incompatible_component_unit_is_reported(tmp_path):
    app = ChefPricingApp(tmp_path)
    app.workspace.write("ingredients", [{
        "id": "ing_001", "name": "Flour", "category": "Dry Goods",
        "purchase_unit": "kg", "purchase_quantity": "1",
        "purchase_price": "10", "base_unit": "g", "base_quantity": "1000",
        "cost_per_base_unit": "0.01", "waste_percent": "0",
        "supplier": "", "last_price_date": "2026-06-12",
        "active": "true", "notes": "",
    }])
    app.workspace.write("dishes", [{
        "id": "dish_001", "name": "Test Dish", "category": "Test",
        "serving_size": "1", "serving_unit": "portion", "total_cost": "0",
        "desired_food_cost_percent": "30", "suggested_price": "0",
        "manual_price": "0", "profit_margin": "0", "active": "true",
        "notes": "",
    }])
    app.workspace.write("dish_components", [{
        "id": "dc_001", "dish_id": "dish_001",
        "component_type": "ingredient", "component_id": "ing_001",
        "quantity": "100", "unit": "ml", "loss_percent": "0", "notes": "",
    }])
    issues = app.validate()
    assert any(
        issue.field == "unit" and "Incompatible" in issue.message
        for issue in issues
    )
