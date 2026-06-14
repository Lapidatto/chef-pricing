class ChefPricingError(Exception):
    """Expected error that can be presented to the user."""


class ValidationError(ChefPricingError):
    pass


class NotFoundError(ChefPricingError):
    pass


class IncompatibleUnitError(ChefPricingError):
    pass
