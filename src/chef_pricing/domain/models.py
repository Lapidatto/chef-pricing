from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal
from typing import ClassVar


def _text(value: object) -> str:
    return "" if value is None else str(value).strip()


def _decimal(value: object, default: str = "0") -> Decimal:
    text = _text(value)
    return Decimal(text if text else default)


def _bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return _text(value).lower() in {"true", "1", "yes", "sim"}


def decimal_text(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.000001")).normalize(), "f")


@dataclass(slots=True)
class CsvModel:
    FIELDS: ClassVar[tuple[str, ...]] = ()

    def to_row(self) -> dict[str, str]:
        row: dict[str, str] = {}
        for key, value in asdict(self).items():
            if isinstance(value, Decimal):
                row[key] = decimal_text(value)
            elif isinstance(value, bool):
                row[key] = str(value).lower()
            else:
                row[key] = str(value)
        return row


@dataclass(slots=True)
class Ingredient(CsvModel):
    FIELDS = (
        "id", "name", "category", "purchase_unit", "purchase_quantity",
        "purchase_price", "base_unit", "base_quantity", "cost_per_base_unit",
        "waste_percent", "supplier", "last_price_date", "active", "notes",
    )
    id: str
    name: str
    category: str
    purchase_unit: str
    purchase_quantity: Decimal
    purchase_price: Decimal
    base_unit: str
    base_quantity: Decimal
    cost_per_base_unit: Decimal
    waste_percent: Decimal = Decimal("0")
    supplier: str = ""
    last_price_date: str = ""
    active: bool = True
    notes: str = ""

    @classmethod
    def from_row(cls, row: dict[str, str]) -> Ingredient:
        return cls(
            id=_text(row.get("id")), name=_text(row.get("name")),
            category=_text(row.get("category")),
            purchase_unit=_text(row.get("purchase_unit")),
            purchase_quantity=_decimal(row.get("purchase_quantity")),
            purchase_price=_decimal(row.get("purchase_price")),
            base_unit=_text(row.get("base_unit")),
            base_quantity=_decimal(row.get("base_quantity")),
            cost_per_base_unit=_decimal(row.get("cost_per_base_unit")),
            waste_percent=_decimal(row.get("waste_percent")),
            supplier=_text(row.get("supplier")),
            last_price_date=_text(row.get("last_price_date")),
            active=_bool(row.get("active")), notes=_text(row.get("notes")),
        )

    @property
    def effective_cost(self) -> Decimal:
        factor = Decimal("1") - self.waste_percent / Decimal("100")
        return self.cost_per_base_unit / factor if factor > 0 else Decimal("0")


@dataclass(slots=True)
class Preparation(CsvModel):
    FIELDS = (
        "id", "name", "category", "yield_quantity", "yield_unit",
        "total_cost", "cost_per_yield_unit", "active", "notes",
    )
    id: str
    name: str
    category: str
    yield_quantity: Decimal
    yield_unit: str
    total_cost: Decimal = Decimal("0")
    cost_per_yield_unit: Decimal = Decimal("0")
    active: bool = True
    notes: str = ""

    @classmethod
    def from_row(cls, row: dict[str, str]) -> Preparation:
        return cls(
            id=_text(row.get("id")), name=_text(row.get("name")),
            category=_text(row.get("category")),
            yield_quantity=_decimal(row.get("yield_quantity")),
            yield_unit=_text(row.get("yield_unit")),
            total_cost=_decimal(row.get("total_cost")),
            cost_per_yield_unit=_decimal(row.get("cost_per_yield_unit")),
            active=_bool(row.get("active")), notes=_text(row.get("notes")),
        )


@dataclass(slots=True)
class Dish(CsvModel):
    FIELDS = (
        "id", "name", "category", "serving_size", "serving_unit",
        "total_cost", "desired_food_cost_percent", "suggested_price",
        "manual_price", "profit_margin", "active", "notes",
    )
    id: str
    name: str
    category: str
    serving_size: Decimal
    serving_unit: str
    total_cost: Decimal = Decimal("0")
    desired_food_cost_percent: Decimal = Decimal("30")
    suggested_price: Decimal = Decimal("0")
    manual_price: Decimal = Decimal("0")
    profit_margin: Decimal = Decimal("0")
    active: bool = True
    notes: str = ""

    @classmethod
    def from_row(cls, row: dict[str, str]) -> Dish:
        return cls(
            id=_text(row.get("id")), name=_text(row.get("name")),
            category=_text(row.get("category")),
            serving_size=_decimal(row.get("serving_size"), "1"),
            serving_unit=_text(row.get("serving_unit")),
            total_cost=_decimal(row.get("total_cost")),
            desired_food_cost_percent=_decimal(
                row.get("desired_food_cost_percent"), "30"
            ),
            suggested_price=_decimal(row.get("suggested_price")),
            manual_price=_decimal(row.get("manual_price")),
            profit_margin=_decimal(row.get("profit_margin")),
            active=_bool(row.get("active")), notes=_text(row.get("notes")),
        )


@dataclass(slots=True)
class RecipeComponent(CsvModel):
    id: str
    parent_id: str
    component_type: str
    component_id: str
    quantity: Decimal
    unit: str
    loss_percent: Decimal = Decimal("0")
    notes: str = ""

    @classmethod
    def from_row(
        cls, row: dict[str, str], parent_field: str
    ) -> RecipeComponent:
        return cls(
            id=_text(row.get("id")), parent_id=_text(row.get(parent_field)),
            component_type=_text(row.get("component_type")),
            component_id=_text(row.get("component_id")),
            quantity=_decimal(row.get("quantity")),
            unit=_text(row.get("unit")),
            loss_percent=_decimal(row.get("loss_percent")),
            notes=_text(row.get("notes")),
        )

    def to_parent_row(self, parent_field: str) -> dict[str, str]:
        return {
            "id": self.id,
            parent_field: self.parent_id,
            "component_type": self.component_type,
            "component_id": self.component_id,
            "quantity": decimal_text(self.quantity),
            "unit": self.unit,
            "loss_percent": decimal_text(self.loss_percent),
            "notes": self.notes,
        }


@dataclass(slots=True)
class Unit(CsvModel):
    FIELDS = ("id", "name", "type", "to_base_factor", "base_unit", "active")
    id: str
    name: str
    type: str
    to_base_factor: Decimal
    base_unit: str
    active: bool = True

    @classmethod
    def from_row(cls, row: dict[str, str]) -> Unit:
        return cls(
            id=_text(row.get("id")), name=_text(row.get("name")),
            type=_text(row.get("type")),
            to_base_factor=_decimal(row.get("to_base_factor"), "1"),
            base_unit=_text(row.get("base_unit")), active=_bool(row.get("active")),
        )


@dataclass(slots=True)
class PriceHistory(CsvModel):
    FIELDS = (
        "id", "ingredient_id", "purchase_unit", "purchase_quantity",
        "purchase_price", "supplier", "price_date", "notes",
    )
    id: str
    ingredient_id: str
    purchase_unit: str
    purchase_quantity: Decimal
    purchase_price: Decimal
    supplier: str
    price_date: str
    notes: str = ""

    @classmethod
    def from_row(cls, row: dict[str, str]) -> PriceHistory:
        return cls(
            id=_text(row.get("id")),
            ingredient_id=_text(row.get("ingredient_id")),
            purchase_unit=_text(row.get("purchase_unit")),
            purchase_quantity=_decimal(row.get("purchase_quantity")),
            purchase_price=_decimal(row.get("purchase_price")),
            supplier=_text(row.get("supplier")),
            price_date=_text(row.get("price_date")),
            notes=_text(row.get("notes")),
        )


@dataclass(slots=True)
class ValidationIssue:
    file: str
    severity: str
    message: str
    line: int | None = None
    field: str = ""
    suggestion: str = ""

