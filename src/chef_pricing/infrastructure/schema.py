from __future__ import annotations

from dataclasses import dataclass

from chef_pricing.domain.models import (
    Dish,
    Ingredient,
    Preparation,
    PriceHistory,
    Unit,
)


@dataclass(frozen=True)
class CsvSchema:
    filename: str
    fields: tuple[str, ...]


COMPONENT_FIELDS = (
    "id", "component_type", "component_id", "quantity", "unit",
    "loss_percent", "notes",
)

SCHEMAS: dict[str, CsvSchema] = {
    "ingredients": CsvSchema("ingredients.csv", Ingredient.FIELDS),
    "preparations": CsvSchema("preparations.csv", Preparation.FIELDS),
    "preparation_components": CsvSchema(
        "preparation_components.csv",
        ("id", "preparation_id", *COMPONENT_FIELDS[1:]),
    ),
    "dishes": CsvSchema("dishes.csv", Dish.FIELDS),
    "dish_components": CsvSchema(
        "dish_components.csv", ("id", "dish_id", *COMPONENT_FIELDS[1:])
    ),
    "units": CsvSchema("units.csv", Unit.FIELDS),
    "price_history": CsvSchema("price_history.csv", PriceHistory.FIELDS),
    "app_settings": CsvSchema("app_settings.csv", ("key", "value")),
}

DEFAULT_ROWS: dict[str, list[dict[str, str]]] = {
    "units": [
        {
            "id": "unit_kg", "name": "kg", "type": "mass",
            "to_base_factor": "1000", "base_unit": "g", "active": "true",
        },
        {
            "id": "unit_g", "name": "g", "type": "mass",
            "to_base_factor": "1", "base_unit": "g", "active": "true",
        },
        {
            "id": "unit_l", "name": "l", "type": "volume",
            "to_base_factor": "1000", "base_unit": "ml", "active": "true",
        },
        {
            "id": "unit_ml", "name": "ml", "type": "volume",
            "to_base_factor": "1", "base_unit": "ml", "active": "true",
        },
        {
            "id": "unit_un", "name": "un", "type": "count",
            "to_base_factor": "1", "base_unit": "un", "active": "true",
        },
    ],
    "app_settings": [
        {"key": "data_version", "value": "1"},
        {"key": "currency", "value": "AUD"},
        {"key": "decimal_separator", "value": "."},
        {"key": "default_food_cost_percent", "value": "30"},
        {"key": "backup_on_startup", "value": "true"},
        {"key": "commercial_rounding", "value": "none"},
    ],
}
