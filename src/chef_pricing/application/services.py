from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from chef_pricing.domain.exceptions import IncompatibleUnitError, ValidationError
from chef_pricing.domain.models import (
    Dish,
    Ingredient,
    Preparation,
    RecipeComponent,
    Unit,
)

HUNDRED = Decimal("100")


class UnitConversionService:
    def __init__(self, units: list[Unit]):
        self.units = {unit.name: unit for unit in units if unit.active}

    def convert(self, quantity: Decimal, source: str, target: str) -> Decimal:
        if source not in self.units or target not in self.units:
            raise IncompatibleUnitError(f"Unknown unit: {source} or {target}.")
        source_unit = self.units[source]
        target_unit = self.units[target]
        if source_unit.type != target_unit.type:
            raise IncompatibleUnitError(
                f"Cannot convert {source} to {target}."
            )
        base_quantity = quantity * source_unit.to_base_factor
        return base_quantity / target_unit.to_base_factor


class PricingService:
    @staticmethod
    def ingredient_base_values(
        purchase_quantity: Decimal,
        purchase_price: Decimal,
        purchase_unit: str,
        conversion: UnitConversionService,
    ) -> tuple[str, Decimal, Decimal]:
        if purchase_quantity <= 0:
            raise ValidationError("Purchase quantity must be greater than zero.")
        if purchase_price < 0:
            raise ValidationError("Purchase price cannot be negative.")
        unit = conversion.units.get(purchase_unit)
        if unit is None:
            raise ValidationError("Select a valid purchase unit.")
        base_quantity = conversion.convert(
            purchase_quantity, purchase_unit, unit.base_unit
        )
        return unit.base_unit, base_quantity, purchase_price / base_quantity

    @staticmethod
    def usage_cost(
        unit_cost: Decimal,
        quantity: Decimal,
        loss_percent: Decimal = Decimal("0"),
    ) -> Decimal:
        if quantity < 0:
            raise ValidationError("Usage quantity cannot be negative.")
        if loss_percent < 0 or loss_percent >= HUNDRED:
            raise ValidationError("Waste must be between 0 and 99.99%.")
        factor = Decimal("1") - loss_percent / HUNDRED
        return quantity * unit_cost / factor

    @staticmethod
    def suggested_price(total_cost: Decimal, food_cost: Decimal) -> Decimal:
        if food_cost <= 0 or food_cost > HUNDRED:
            raise ValidationError("Food cost must be between 0 and 100%.")
        return total_cost / (food_cost / HUNDRED)

    @staticmethod
    def profit_margin(total_cost: Decimal, selling_price: Decimal) -> Decimal:
        if selling_price <= 0:
            return Decimal("0")
        return (selling_price - total_cost) / selling_price * HUNDRED

    @staticmethod
    def commercial_round(value: Decimal, strategy: str) -> Decimal:
        if strategy == "x.90":
            whole = value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
            candidate = whole - Decimal("0.10")
            return candidate if candidate >= value else candidate + Decimal("1")
        if strategy == "integer":
            return value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class RecipeCostService:
    def __init__(
        self,
        ingredients: dict[str, Ingredient],
        preparations: dict[str, Preparation],
        conversion: UnitConversionService,
    ):
        self.ingredients = ingredients
        self.preparations = preparations
        self.conversion = conversion

    def component_cost(self, component: RecipeComponent) -> Decimal:
        if component.component_type == "ingredient":
            item = self.ingredients.get(component.component_id)
            if item is None:
                raise ValidationError(
                    f"Ingredient not found: {component.component_id}"
                )
            quantity = self.conversion.convert(
                component.quantity, component.unit, item.base_unit
            )
            combined_loss = (
                Decimal("1") -
                (Decimal("1") - item.waste_percent / HUNDRED) *
                (Decimal("1") - component.loss_percent / HUNDRED)
            ) * HUNDRED
            return PricingService.usage_cost(
                item.cost_per_base_unit, quantity, combined_loss
            )
        if component.component_type == "preparation":
            item = self.preparations.get(component.component_id)
            if item is None:
                raise ValidationError(
                    f"Preparation not found: {component.component_id}"
                )
            quantity = self.conversion.convert(
                component.quantity, component.unit, item.yield_unit
            )
            return PricingService.usage_cost(
                item.cost_per_yield_unit, quantity, component.loss_percent
            )
        raise ValidationError(f"Invalid component type: {component.component_type}")

    def total(self, components: list[RecipeComponent]) -> Decimal:
        return sum((self.component_cost(item) for item in components), Decimal("0"))
