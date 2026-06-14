from decimal import Decimal

import pytest

from chef_pricing.application.services import UnitConversionService
from chef_pricing.domain.exceptions import IncompatibleUnitError
from chef_pricing.domain.models import Unit


@pytest.fixture
def conversion():
    return UnitConversionService([
        Unit("kg", "kg", "mass", Decimal("1000"), "g"),
        Unit("g", "g", "mass", Decimal("1"), "g"),
        Unit("l", "l", "volume", Decimal("1000"), "ml"),
        Unit("ml", "ml", "volume", Decimal("1"), "ml"),
    ])


def test_converts_kg_to_g(conversion):
    assert conversion.convert(Decimal("1.5"), "kg", "g") == Decimal("1500")


def test_rejects_incompatible_units(conversion):
    with pytest.raises(IncompatibleUnitError):
        conversion.convert(Decimal("1"), "kg", "ml")

