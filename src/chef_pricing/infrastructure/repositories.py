from __future__ import annotations

from dataclasses import replace
from typing import Generic, TypeVar

from chef_pricing.domain.exceptions import NotFoundError
from chef_pricing.domain.models import (
    CsvModel,
    Dish,
    Ingredient,
    Preparation,
    PriceHistory,
    RecipeComponent,
    Unit,
)
from chef_pricing.infrastructure.csv_storage import CsvWorkspace

T = TypeVar("T", bound=CsvModel)


class ModelRepository(Generic[T]):
    def __init__(self, workspace: CsvWorkspace, key: str, model_type: type[T]):
        self.workspace = workspace
        self.key = key
        self.model_type = model_type

    def list_all(self) -> list[T]:
        try:
            rows = self.workspace.read(self.key)
        except NotFoundError:
            return []
        return [self.model_type.from_row(row) for row in rows]

    def get(self, item_id: str) -> T:
        for item in self.list_all():
            if getattr(item, "id") == item_id:
                return item
        raise NotFoundError(f"Record not found: {item_id}")

    def save(self, item: T) -> T:
        rows = self.list_all()
        if any(getattr(existing, "id") == getattr(item, "id") for existing in rows):
            raise ValueError(f"Duplicate ID: {getattr(item, 'id')}")
        rows.append(item)
        self.workspace.write(self.key, [entry.to_row() for entry in rows])
        return item

    def update(self, item: T) -> T:
        rows = self.list_all()
        for index, existing in enumerate(rows):
            if getattr(existing, "id") == getattr(item, "id"):
                rows[index] = item
                self.workspace.write(self.key, [entry.to_row() for entry in rows])
                return item
        raise NotFoundError(f"Record not found: {getattr(item, 'id')}")

    def set_active(self, item_id: str, active: bool) -> T:
        item = self.get(item_id)
        updated = replace(item, active=active)
        return self.update(updated)


class ComponentRepository:
    def __init__(self, workspace: CsvWorkspace, key: str, parent_field: str):
        self.workspace = workspace
        self.key = key
        self.parent_field = parent_field

    def list_all(self) -> list[RecipeComponent]:
        try:
            rows = self.workspace.read(self.key)
        except NotFoundError:
            return []
        return [
            RecipeComponent.from_row(row, self.parent_field)
            for row in rows
        ]

    def list_for(self, parent_id: str) -> list[RecipeComponent]:
        return [item for item in self.list_all() if item.parent_id == parent_id]

    def replace_for(
        self, parent_id: str, components: list[RecipeComponent]
    ) -> None:
        retained = [
            item for item in self.list_all() if item.parent_id != parent_id
        ]
        rows = retained + components
        self.workspace.write(
            self.key,
            [item.to_parent_row(self.parent_field) for item in rows],
        )


class Repositories:
    def __init__(self, workspace: CsvWorkspace):
        self.ingredients = ModelRepository(workspace, "ingredients", Ingredient)
        self.preparations = ModelRepository(workspace, "preparations", Preparation)
        self.dishes = ModelRepository(workspace, "dishes", Dish)
        self.units = ModelRepository(workspace, "units", Unit)
        self.price_history = ModelRepository(
            workspace, "price_history", PriceHistory
        )
        self.preparation_components = ComponentRepository(
            workspace, "preparation_components", "preparation_id"
        )
        self.dish_components = ComponentRepository(
            workspace, "dish_components", "dish_id"
        )
