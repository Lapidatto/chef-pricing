from __future__ import annotations

import os
from decimal import Decimal, InvalidOperation
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from chef_pricing.application.app_service import ChefPricingApp
from chef_pricing.domain.exceptions import ChefPricingError
from chef_pricing.domain.models import Dish, Ingredient, Preparation, decimal_text


def money(value: Decimal) -> str:
    return f"${value.quantize(Decimal('0.01')):,.2f}"


def spin(maximum: float = 1_000_000, decimals: int = 3) -> QDoubleSpinBox:
    widget = QDoubleSpinBox()
    widget.setRange(0, maximum)
    widget.setDecimals(decimals)
    widget.setGroupSeparatorShown(True)
    return widget


class IngredientDialog(QDialog):
    def __init__(self, units: list[str], item: Ingredient | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Ingredient" if item else "New Ingredient")
        self.setMinimumWidth(520)
        form = QFormLayout(self)
        self.name = QLineEdit(item.name if item else "")
        self.category = QLineEdit(item.category if item else "")
        self.purchase_unit = QComboBox()
        self.purchase_unit.addItems(units)
        self.quantity = spin()
        self.price = spin(decimals=2)
        self.waste = spin(99.99, 2)
        self.supplier = QLineEdit(item.supplier if item else "")
        self.price_date = QLineEdit(item.last_price_date if item else "")
        self.price_date.setPlaceholderText("YYYY-MM-DD (blank = today)")
        self.active = QCheckBox("Active ingredient")
        self.active.setChecked(item.active if item else True)
        self.notes = QTextEdit(item.notes if item else "")
        self.notes.setMaximumHeight(80)
        if item:
            self.purchase_unit.setCurrentText(item.purchase_unit)
            self.quantity.setValue(float(item.purchase_quantity))
            self.price.setValue(float(item.purchase_price))
            self.waste.setValue(float(item.waste_percent))
        else:
            self.quantity.setValue(1)
        for label, widget in (
            ("Name *", self.name), ("Category", self.category),
            ("Purchase unit *", self.purchase_unit),
            ("Purchased quantity *", self.quantity),
            ("Purchase price *", self.price), ("Waste (%)", self.waste),
            ("Supplier", self.supplier), ("Price date", self.price_date),
            ("Status", self.active), ("Notes", self.notes),
        ):
            form.addRow(label, widget)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def values(self) -> dict:
        return {
            "name": self.name.text(), "category": self.category.text(),
            "purchase_unit": self.purchase_unit.currentText(),
            "purchase_quantity": Decimal(str(self.quantity.value())),
            "purchase_price": Decimal(str(self.price.value())),
            "waste_percent": Decimal(str(self.waste.value())),
            "supplier": self.supplier.text(),
            "last_price_date": self.price_date.text(),
            "active": self.active.isChecked(),
            "notes": self.notes.toPlainText(),
        }


class PreparationDialog(QDialog):
    def __init__(self, units: list[str], item: Preparation | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(
            "Edit In-house Preparation" if item else "New In-house Preparation"
        )
        self.setMinimumWidth(500)
        form = QFormLayout(self)
        self.name = QLineEdit(item.name if item else "")
        self.category = QLineEdit(item.category if item else "")
        self.yield_quantity = spin()
        self.yield_quantity.setValue(float(item.yield_quantity) if item else 1)
        self.yield_unit = QComboBox()
        self.yield_unit.addItems(units)
        if item:
            self.yield_unit.setCurrentText(item.yield_unit)
        self.active = QCheckBox("Active preparation")
        self.active.setChecked(item.active if item else True)
        self.notes = QTextEdit(item.notes if item else "")
        self.notes.setMaximumHeight(80)
        for label, widget in (
            ("Name *", self.name), ("Category", self.category),
            ("Yield *", self.yield_quantity),
            ("Yield unit *", self.yield_unit),
            ("Status", self.active), ("Notes", self.notes),
        ):
            form.addRow(label, widget)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def values(self) -> dict:
        return {
            "name": self.name.text(), "category": self.category.text(),
            "yield_quantity": Decimal(str(self.yield_quantity.value())),
            "yield_unit": self.yield_unit.currentText(),
            "active": self.active.isChecked(), "notes": self.notes.toPlainText(),
        }


class DishDialog(QDialog):
    def __init__(self, item: Dish | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Dish" if item else "New Dish")
        self.setMinimumWidth(500)
        form = QFormLayout(self)
        self.name = QLineEdit(item.name if item else "")
        self.category = QLineEdit(item.category if item else "")
        self.serving_size = spin()
        self.serving_size.setValue(float(item.serving_size) if item else 1)
        self.serving_unit = QComboBox()
        self.serving_unit.addItems(["portion", "g", "ml", "un"])
        self.food_cost = spin(100, 2)
        self.food_cost.setValue(float(item.desired_food_cost_percent) if item else 30)
        self.manual_price = spin(decimals=2)
        self.manual_price.setValue(float(item.manual_price) if item else 0)
        self.active = QCheckBox("Active dish")
        self.active.setChecked(item.active if item else True)
        self.notes = QTextEdit(item.notes if item else "")
        self.notes.setMaximumHeight(80)
        if item:
            self.serving_unit.setCurrentText(item.serving_unit)
        for label, widget in (
            ("Name *", self.name), ("Category", self.category),
            ("Serving size *", self.serving_size),
            ("Serving unit", self.serving_unit),
            ("Target food cost (%) *", self.food_cost),
            ("Manual price", self.manual_price),
            ("Status", self.active), ("Notes", self.notes),
        ):
            form.addRow(label, widget)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def values(self) -> dict:
        return {
            "name": self.name.text(), "category": self.category.text(),
            "serving_size": Decimal(str(self.serving_size.value())),
            "serving_unit": self.serving_unit.currentText(),
            "food_cost": Decimal(str(self.food_cost.value())),
            "manual_price": Decimal(str(self.manual_price.value())),
            "active": self.active.isChecked(), "notes": self.notes.toPlainText(),
        }


class ComponentDialog(QDialog):
    def __init__(
        self, app: ChefPricingApp, parent_type: str, parent_id: str, parent=None
    ):
        super().__init__(parent)
        self.app = app
        self.parent_type = parent_type
        self.parent_id = parent_id
        self.options = app.component_options(parent_type)
        self.setWindowTitle("Recipe Sheet / Composition")
        self.resize(880, 540)
        layout = QVBoxLayout(self)
        help_label = QLabel(
            "Add the components used. Costs are recalculated when the recipe is saved."
        )
        help_label.setObjectName("muted")
        layout.addWidget(help_label)
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Type", "Component", "Quantity", "Unit", "Waste %", "Notes"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)
        actions = QHBoxLayout()
        add_button = QPushButton("+ Add Component")
        remove_button = QPushButton("Remove Selected")
        add_button.clicked.connect(self.add_row)
        remove_button.clicked.connect(self.remove_rows)
        actions.addWidget(add_button)
        actions.addWidget(remove_button)
        actions.addStretch()
        layout.addLayout(actions)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        repository = (
            app.repos.preparation_components
            if parent_type == "preparation" else app.repos.dish_components
        )
        for component in repository.list_for(parent_id):
            self.add_row(component)

    def add_row(self, component=None) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        selector = QComboBox()
        for component_type, component_id, name, unit in self.options:
            selector.addItem(
                f"{'Ingredient' if component_type == 'ingredient' else 'Preparation'} | {name}",
                (component_type, component_id, unit),
            )
        if component:
            for index in range(selector.count()):
                if selector.itemData(index)[1] == component.component_id:
                    selector.setCurrentIndex(index)
                    break
        type_label = QLabel()
        unit_combo = QComboBox()
        unit_combo.addItems([unit.name for unit in self.app.repos.units.list_all()])

        def update_option(index: int) -> None:
            data = selector.itemData(index)
            if data:
                type_label.setText(
                    "Ingredient" if data[0] == "ingredient" else "Preparation"
                )
                if not component:
                    unit_combo.setCurrentText(data[2])

        selector.currentIndexChanged.connect(update_option)
        quantity = spin()
        quantity.setValue(float(component.quantity) if component else 1)
        loss = spin(99.99, 2)
        loss.setValue(float(component.loss_percent) if component else 0)
        notes = QLineEdit(component.notes if component else "")
        if component:
            unit_combo.setCurrentText(component.unit)
        self.table.setCellWidget(row, 0, type_label)
        self.table.setCellWidget(row, 1, selector)
        self.table.setCellWidget(row, 2, quantity)
        self.table.setCellWidget(row, 3, unit_combo)
        self.table.setCellWidget(row, 4, loss)
        self.table.setCellWidget(row, 5, notes)
        update_option(selector.currentIndex())

    def remove_rows(self) -> None:
        rows = sorted({index.row() for index in self.table.selectedIndexes()}, reverse=True)
        for row in rows:
            self.table.removeRow(row)

    def values(self) -> list[dict[str, object]]:
        rows = []
        for row in range(self.table.rowCount()):
            selector: QComboBox = self.table.cellWidget(row, 1)
            quantity: QDoubleSpinBox = self.table.cellWidget(row, 2)
            unit: QComboBox = self.table.cellWidget(row, 3)
            loss: QDoubleSpinBox = self.table.cellWidget(row, 4)
            notes: QLineEdit = self.table.cellWidget(row, 5)
            data = selector.currentData()
            if not data:
                continue
            rows.append({
                "component_type": data[0], "component_id": data[1],
                "quantity": Decimal(str(quantity.value())),
                "unit": unit.currentText(),
                "loss_percent": Decimal(str(loss.value())),
                "notes": notes.text(),
            })
        return rows


class MainWindow(QMainWindow):
    NAVIGATION = (
        "Overview", "Ingredients", "In-house Preparations", "Dishes",
        "Reports", "Validation", "Settings",
    )

    def __init__(self, app: ChefPricingApp):
        super().__init__()
        self.app = app
        self.setWindowTitle("Chef Pricing - Costing and Pricing")
        self.resize(1280, 780)
        root = QWidget()
        self.setCentralWidget(root)
        shell = QHBoxLayout(root)
        shell.setContentsMargins(0, 0, 0, 0)
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(230)
        side_layout = QVBoxLayout(sidebar)
        brand = QLabel("CHEF PRICING")
        brand.setObjectName("brand")
        subtitle = QLabel("Kitchen cost control")
        subtitle.setObjectName("sidebarMuted")
        side_layout.addWidget(brand)
        side_layout.addWidget(subtitle)
        side_layout.addSpacing(24)
        self.nav = QListWidget()
        self.nav.addItems(self.NAVIGATION)
        self.nav.setCurrentRow(0)
        self.nav.currentRowChanged.connect(self.change_page)
        side_layout.addWidget(self.nav)
        side_layout.addStretch()
        workspace = QLabel(str(self.app.workspace.root))
        workspace.setWordWrap(True)
        workspace.setObjectName("sidebarMuted")
        side_layout.addWidget(QLabel("Workspace"))
        side_layout.addWidget(workspace)
        shell.addWidget(sidebar)
        self.pages = QStackedWidget()
        shell.addWidget(self.pages, 1)
        for builder in (
            self.build_dashboard, self.build_ingredients,
            self.build_preparations, self.build_dishes, self.build_reports,
            self.build_validation, self.build_settings,
        ):
            self.pages.addWidget(builder())
        self.refresh_all()

    def page(self, title: str, description: str) -> tuple[QWidget, QVBoxLayout]:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 28, 32, 28)
        heading = QLabel(title)
        heading.setObjectName("pageTitle")
        copy = QLabel(description)
        copy.setObjectName("muted")
        layout.addWidget(heading)
        layout.addWidget(copy)
        layout.addSpacing(14)
        return widget, layout

    def build_dashboard(self) -> QWidget:
        page, layout = self.page(
            "Overview", "Essential numbers for making menu pricing decisions."
        )
        self.cards_layout = QGridLayout()
        self.card_values: dict[str, QLabel] = {}
        cards = (
            ("ingredients", "Active ingredients"),
            ("preparations", "In-house preparations"),
            ("dishes", "Active dishes"),
            ("dishes_without_price", "Dishes without a price"),
            ("ingredients_without_price", "Ingredients without a price"),
            ("issue_count", "File alerts"),
        )
        for index, (key, label) in enumerate(cards):
            card = QFrame()
            card.setObjectName("card")
            card_layout = QVBoxLayout(card)
            value = QLabel("0")
            value.setObjectName("cardValue")
            card_layout.addWidget(value)
            card_layout.addWidget(QLabel(label))
            self.card_values[key] = value
            self.cards_layout.addWidget(card, index // 3, index % 3)
        layout.addLayout(self.cards_layout)
        layout.addWidget(QLabel("Latest price updates"))
        self.history_table = QTableWidget(0, 4)
        self.history_table.setHorizontalHeaderLabels(
            ["Date", "Ingredient", "Supplier", "Price"]
        )
        self.history_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        layout.addWidget(self.history_table)
        return page

    def table_page(
        self, title: str, description: str, headers: list[str]
    ) -> tuple[QWidget, QVBoxLayout, QTableWidget, QHBoxLayout]:
        page, layout = self.page(title, description)
        actions = QHBoxLayout()
        layout.addLayout(actions)
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.doubleClicked.connect(lambda: self.edit_current())
        layout.addWidget(table)
        return page, layout, table, actions

    def build_ingredients(self) -> QWidget:
        page, _, self.ingredients_table, actions = self.table_page(
            "Ingredients",
            "Record purchases, waste, and suppliers. Price changes are kept in history.",
            ["Name", "Category", "Purchase", "Price", "Base cost", "Waste", "Status"],
        )
        new = QPushButton("+ New Ingredient")
        edit = QPushButton("Edit")
        toggle = QPushButton("Activate / Deactivate")
        history = QPushButton("View History")
        new.clicked.connect(lambda: self.edit_ingredient(None))
        edit.clicked.connect(lambda: self.edit_ingredient(self.selected_id(self.ingredients_table)))
        toggle.clicked.connect(lambda: self.toggle_active("ingredient"))
        history.clicked.connect(self.show_ingredient_history)
        for button in (new, edit, toggle, history):
            actions.addWidget(button)
        actions.addStretch()
        return page

    def build_preparations(self) -> QWidget:
        page, _, self.preparations_table, actions = self.table_page(
            "In-house Preparations",
            "Sauces, doughs, and bases made in the kitchen with yield and unit cost.",
            ["Name", "Category", "Yield", "Total cost", "Unit cost", "Status"],
        )
        new = QPushButton("+ New Preparation")
        edit = QPushButton("Edit")
        composition = QPushButton("Edit Composition")
        recalculate = QPushButton("Recalculate")
        toggle = QPushButton("Activate / Deactivate")
        new.clicked.connect(lambda: self.edit_preparation(None))
        edit.clicked.connect(
            lambda: self.edit_preparation(self.selected_id(self.preparations_table))
        )
        composition.clicked.connect(lambda: self.edit_components("preparation"))
        recalculate.clicked.connect(self.recalculate_selected_preparation)
        toggle.clicked.connect(lambda: self.toggle_active("preparation"))
        for button in (new, edit, composition, recalculate, toggle):
            actions.addWidget(button)
        actions.addStretch()
        return page

    def build_dishes(self) -> QWidget:
        page, _, self.dishes_table, actions = self.table_page(
            "Dishes",
            "Build recipe sheets and compare cost, suggested price, and estimated margin.",
            ["Name", "Category", "Cost", "Food cost", "Suggested", "Manual", "Margin"],
        )
        new = QPushButton("+ New Dish")
        edit = QPushButton("Edit")
        composition = QPushButton("Edit Recipe Sheet")
        recalculate = QPushButton("Recalculate")
        export = QPushButton("Export Recipe Sheet")
        toggle = QPushButton("Activate / Deactivate")
        new.clicked.connect(lambda: self.edit_dish(None))
        edit.clicked.connect(lambda: self.edit_dish(self.selected_id(self.dishes_table)))
        composition.clicked.connect(lambda: self.edit_components("dish"))
        recalculate.clicked.connect(self.recalculate_selected_dish)
        export.clicked.connect(self.export_selected_dish)
        toggle.clicked.connect(lambda: self.toggle_active("dish"))
        for button in (new, edit, composition, recalculate, export, toggle):
            actions.addWidget(button)
        actions.addStretch()
        return page

    def build_reports(self) -> QWidget:
        page, layout = self.page(
            "Reports", "Review margins and export data to Excel."
        )
        actions = QHBoxLayout()
        export = QPushButton("Export Dish List")
        open_folder = QPushButton("Open Exports Folder")
        export.clicked.connect(self.export_dishes)
        open_folder.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.app.workspace.exports_dir)))
        )
        actions.addWidget(export)
        actions.addWidget(open_folder)
        actions.addStretch()
        layout.addLayout(actions)
        self.report_table = QTableWidget(0, 6)
        self.report_table.setHorizontalHeaderLabels(
            ["Dish", "Category", "Cost", "Selling price", "Margin", "Assessment"]
        )
        self.report_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        layout.addWidget(self.report_table)
        return page

    def build_validation(self) -> QWidget:
        page, layout = self.page(
            "File Validation",
            "Errors block calculations; warnings identify data that needs review.",
        )
        actions = QHBoxLayout()
        validate = QPushButton("Validate Now")
        recreate = QPushButton("Recreate Missing Files")
        validate.clicked.connect(self.refresh_validation)
        recreate.clicked.connect(self.recreate_files)
        actions.addWidget(validate)
        actions.addWidget(recreate)
        actions.addStretch()
        layout.addLayout(actions)
        self.validation_table = QTableWidget(0, 6)
        self.validation_table.setHorizontalHeaderLabels(
            ["Severity", "File", "Line", "Field", "Issue", "Suggestion"]
        )
        self.validation_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        layout.addWidget(self.validation_table)
        return page

    def build_settings(self) -> QWidget:
        page, layout = self.page(
            "Settings", "Workspace preferences, backups, and price rounding."
        )
        form = QFormLayout()
        self.currency = QLineEdit()
        self.default_food_cost = QSpinBox()
        self.default_food_cost.setRange(1, 100)
        self.rounding = QComboBox()
        self.rounding.addItem("Exact cents", "none")
        self.rounding.addItem("End in .90", "x.90")
        self.rounding.addItem("Nearest whole number", "integer")
        self.backup_startup = QCheckBox("Create backup on startup")
        form.addRow("Currency", self.currency)
        form.addRow("Default food cost (%)", self.default_food_cost)
        form.addRow("Commercial rounding", self.rounding)
        form.addRow("Automatic backup", self.backup_startup)
        layout.addLayout(form)
        actions = QHBoxLayout()
        save = QPushButton("Save Settings")
        backup = QPushButton("Create Backup Now")
        open_data = QPushButton("Open CSV Folder")
        save.clicked.connect(self.save_settings)
        backup.clicked.connect(self.create_backup)
        open_data.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.app.workspace.data_dir)))
        )
        for button in (save, backup, open_data):
            actions.addWidget(button)
        actions.addStretch()
        layout.addLayout(actions)
        self.backups_list = QListWidget()
        layout.addWidget(QLabel("Available backups"))
        layout.addWidget(self.backups_list)
        restore = QPushButton("Restore Selected Backup")
        restore.clicked.connect(self.restore_backup)
        layout.addWidget(restore)
        return page

    def change_page(self, index: int) -> None:
        self.pages.setCurrentIndex(index)
        self.refresh_all()

    def selected_id(self, table: QTableWidget) -> str | None:
        row = table.currentRow()
        if row < 0:
            return None
        item = table.item(row, 0)
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def require_id(self, table: QTableWidget) -> str | None:
        item_id = self.selected_id(table)
        if not item_id:
            QMessageBox.information(self, "Select an Item", "Select a row first.")
        return item_id

    def edit_current(self) -> None:
        index = self.pages.currentIndex()
        if index == 1:
            self.edit_ingredient(self.selected_id(self.ingredients_table))
        elif index == 2:
            self.edit_preparation(self.selected_id(self.preparations_table))
        elif index == 3:
            self.edit_dish(self.selected_id(self.dishes_table))

    def perform(self, action, success: str | None = None):
        try:
            result = action()
            if success:
                QMessageBox.information(self, "Completed", success)
            self.refresh_all()
            return result
        except (ChefPricingError, ValueError, InvalidOperation, OSError) as exc:
            QMessageBox.critical(self, "Unable to Complete", str(exc))
            return None

    def edit_ingredient(self, item_id: str | None) -> None:
        item = self.app.repos.ingredients.get(item_id) if item_id else None
        dialog = IngredientDialog(
            [unit.name for unit in self.app.repos.units.list_all()], item, self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.perform(
                lambda: self.app.save_ingredient(item_id=item_id, **dialog.values())
            )

    def edit_preparation(self, item_id: str | None) -> None:
        item = self.app.repos.preparations.get(item_id) if item_id else None
        dialog = PreparationDialog(
            [unit.name for unit in self.app.repos.units.list_all()], item, self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            saved = self.perform(
                lambda: self.app.save_preparation(item_id=item_id, **dialog.values())
            )
            if saved and not item_id:
                self.open_components("preparation", saved.id)

    def edit_dish(self, item_id: str | None) -> None:
        item = self.app.repos.dishes.get(item_id) if item_id else None
        dialog = DishDialog(item, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            saved = self.perform(
                lambda: self.app.save_dish(item_id=item_id, **dialog.values())
            )
            if saved and not item_id:
                self.open_components("dish", saved.id)

    def edit_components(self, parent_type: str) -> None:
        table = self.preparations_table if parent_type == "preparation" else self.dishes_table
        item_id = self.require_id(table)
        if item_id:
            self.open_components(parent_type, item_id)

    def open_components(self, parent_type: str, item_id: str) -> None:
        if not self.app.component_options(parent_type):
            QMessageBox.warning(
                self, "No Components Available",
                "Create at least one ingredient before building a recipe sheet.",
            )
            return
        dialog = ComponentDialog(self.app, parent_type, item_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.perform(
                lambda: self.app.save_components(parent_type, item_id, dialog.values()),
                "Recipe sheet saved and costs recalculated.",
            )

    def toggle_active(self, entity: str) -> None:
        table = {
            "ingredient": self.ingredients_table,
            "preparation": self.preparations_table,
            "dish": self.dishes_table,
        }[entity]
        repository = {
            "ingredient": self.app.repos.ingredients,
            "preparation": self.app.repos.preparations,
            "dish": self.app.repos.dishes,
        }[entity]
        item_id = self.require_id(table)
        if not item_id:
            return
        item = repository.get(item_id)
        self.perform(lambda: repository.set_active(item_id, not item.active))

    def recalculate_selected_preparation(self) -> None:
        item_id = self.require_id(self.preparations_table)
        if item_id:
            self.perform(lambda: self.app.recalculate_preparation(item_id), "Cost recalculated.")

    def recalculate_selected_dish(self) -> None:
        item_id = self.require_id(self.dishes_table)
        if item_id:
            self.perform(lambda: self.app.recalculate_dish(item_id), "Cost recalculated.")

    def export_selected_dish(self) -> None:
        item_id = self.require_id(self.dishes_table)
        if item_id:
            path = self.perform(lambda: self.app.export_dish_sheet(item_id))
            if path:
                QMessageBox.information(self, "Recipe Sheet Exported", str(path))

    def export_dishes(self) -> None:
        path = self.perform(self.app.export_dishes)
        if path:
            QMessageBox.information(self, "Report Exported", str(path))

    def show_ingredient_history(self) -> None:
        item_id = self.require_id(self.ingredients_table)
        if not item_id:
            return
        ingredient = self.app.repos.ingredients.get(item_id)
        entries = [
            item for item in self.app.repos.price_history.list_all()
            if item.ingredient_id == item_id
        ]
        text = "\n".join(
            f"{item.price_date}: {money(item.purchase_price)} for "
            f"{decimal_text(item.purchase_quantity)} {item.purchase_unit} - {item.supplier}"
            for item in sorted(entries, key=lambda entry: entry.price_date, reverse=True)
        ) or "No records found."
        QMessageBox.information(self, f"History - {ingredient.name}", text)

    def refresh_all(self) -> None:
        self.refresh_dashboard()
        self.refresh_ingredients()
        self.refresh_preparations()
        self.refresh_dishes()
        self.refresh_reports()
        self.refresh_validation()
        self.refresh_settings()

    @staticmethod
    def populate(table: QTableWidget, rows: list[tuple[str, list[str]]]) -> None:
        table.setRowCount(len(rows))
        for row_index, (item_id, values) in enumerate(rows):
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 0:
                    item.setData(Qt.ItemDataRole.UserRole, item_id)
                table.setItem(row_index, column, item)

    def refresh_dashboard(self) -> None:
        data = self.app.dashboard()
        for key, label in self.card_values.items():
            value = len(data["issues"]) if key == "issue_count" else data[key]
            label.setText(str(value))
        ingredient_names = {
            item.id: item.name for item in self.app.repos.ingredients.list_all()
        }
        rows = [
            (
                entry.id,
                [
                    entry.price_date, ingredient_names.get(entry.ingredient_id, entry.ingredient_id),
                    entry.supplier, money(entry.purchase_price),
                ],
            )
            for entry in data["history"]
        ]
        self.populate(self.history_table, rows)

    def refresh_ingredients(self) -> None:
        rows = []
        for item in self.app.repos.ingredients.list_all():
            rows.append((item.id, [
                item.name, item.category,
                f"{decimal_text(item.purchase_quantity)} {item.purchase_unit}",
                money(item.purchase_price),
                f"{money(item.cost_per_base_unit)}/{item.base_unit}",
                f"{decimal_text(item.waste_percent)}%",
                "Active" if item.active else "Inactive",
            ]))
        self.populate(self.ingredients_table, rows)

    def refresh_preparations(self) -> None:
        rows = [
            (item.id, [
                item.name, item.category,
                f"{decimal_text(item.yield_quantity)} {item.yield_unit}",
                money(item.total_cost),
                f"{money(item.cost_per_yield_unit)}/{item.yield_unit}",
                "Active" if item.active else "Inactive",
            ])
            for item in self.app.repos.preparations.list_all()
        ]
        self.populate(self.preparations_table, rows)

    def refresh_dishes(self) -> None:
        rows = [
            (item.id, [
                item.name, item.category, money(item.total_cost),
                f"{decimal_text(item.desired_food_cost_percent)}%",
                money(item.suggested_price), money(item.manual_price),
                f"{item.profit_margin.quantize(Decimal('0.1'))}%",
            ])
            for item in self.app.repos.dishes.list_all()
        ]
        self.populate(self.dishes_table, rows)

    def refresh_reports(self) -> None:
        rows = []
        for item in self.app.repos.dishes.list_all():
            price = item.manual_price if item.manual_price > 0 else item.suggested_price
            diagnostic = (
                "Below cost" if price < item.total_cost
                else "Low margin" if item.profit_margin < 50
                else "Healthy"
            )
            rows.append((item.id, [
                item.name, item.category, money(item.total_cost), money(price),
                f"{item.profit_margin.quantize(Decimal('0.1'))}%", diagnostic,
            ]))
        self.populate(self.report_table, rows)

    def refresh_validation(self) -> None:
        issues = self.app.validate()
        rows = [
            (f"{issue.file}:{issue.line}", [
                "ERROR" if issue.severity == "error" else "WARNING",
                issue.file, str(issue.line or "-"), issue.field,
                issue.message, issue.suggestion,
            ])
            for issue in issues
        ]
        self.populate(self.validation_table, rows)

    def recreate_files(self) -> None:
        self.perform(self.app.workspace.initialize, "Missing files were recreated.")

    def refresh_settings(self) -> None:
        settings = self.app.workspace.settings()
        self.currency.setText(settings.get("currency", "AUD"))
        self.default_food_cost.setValue(
            int(settings.get("default_food_cost_percent", "30"))
        )
        index = self.rounding.findData(settings.get("commercial_rounding", "none"))
        self.rounding.setCurrentIndex(max(index, 0))
        self.backup_startup.setChecked(settings.get("backup_on_startup") == "true")
        self.backups_list.clear()
        for path in self.app.workspace.list_backups():
            item = QListWidgetItem(path.name)
            item.setData(Qt.ItemDataRole.UserRole, str(path))
            self.backups_list.addItem(item)

    def save_settings(self) -> None:
        def save():
            self.app.workspace.update_setting("currency", self.currency.text() or "AUD")
            self.app.workspace.update_setting(
                "default_food_cost_percent", str(self.default_food_cost.value())
            )
            self.app.workspace.update_setting(
                "commercial_rounding", str(self.rounding.currentData())
            )
            self.app.workspace.update_setting(
                "backup_on_startup",
                str(self.backup_startup.isChecked()).lower(),
            )
            self.app.recalculate_all_dishes()
        self.perform(save, "Settings saved.")

    def create_backup(self) -> None:
        path = self.perform(self.app.workspace.backup)
        if path:
            QMessageBox.information(self, "Backup Created", str(path))

    def restore_backup(self) -> None:
        item = self.backups_list.currentItem()
        if not item:
            QMessageBox.information(
                self, "Select a Backup", "Choose a backup from the list."
            )
            return
        answer = QMessageBox.question(
            self, "Restore Backup",
            "The current CSV files will be replaced. Continue?",
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.perform(
                lambda: self.app.workspace.restore(item.data(Qt.ItemDataRole.UserRole)),
                "Backup restored.",
            )
