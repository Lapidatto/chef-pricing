from decimal import Decimal

import pytest

from chef_pricing.application.services import PricingService


def test_ingredient_usage_cost_without_loss():
    assert PricingService.usage_cost(
        Decimal("0.08"), Decimal("15")
    ) == Decimal("1.20")


def test_ingredient_usage_cost_with_loss():
    result = PricingService.usage_cost(
        Decimal("0.018"), Decimal("1000"), Decimal("10")
    )
    assert result == Decimal("20")


def test_suggested_price_and_margin():
    suggested = PricingService.suggested_price(Decimal("4.85"), Decimal("30"))
    assert suggested.quantize(Decimal("0.01")) == Decimal("16.17")
    margin = PricingService.profit_margin(Decimal("4.85"), Decimal("16.17"))
    assert margin.quantize(Decimal("0.01")) == Decimal("70.01")


def test_commercial_rounding():
    assert PricingService.commercial_round(Decimal("16.17"), "x.90") == Decimal("16.90")
    assert PricingService.commercial_round(Decimal("16.60"), "integer") == Decimal("17")


def test_invalid_food_cost_is_rejected():
    with pytest.raises(Exception):
        PricingService.suggested_price(Decimal("10"), Decimal("0"))

