from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QSettings, QStandardPaths
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from chef_pricing.application.app_service import ChefPricingApp
from chef_pricing.frontend.main_window import MainWindow
from chef_pricing.infrastructure.csv_storage import ensure_writable_directory
from chef_pricing.product import PRODUCT_NAME, PUBLISHER, default_workspace_path, resource_path


class WelcomeDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome to Chef Pricing")
        self.setMinimumWidth(620)
        layout = QVBoxLayout(self)
        title = QLabel("Organize your kitchen costs")
        title.setObjectName("pageTitle")
        description = QLabel(
            "Choose a folder for the CSV files. They can be opened in Excel "
            "and will be validated whenever the application starts."
        )
        description.setWordWrap(True)
        description.setObjectName("muted")
        layout.addWidget(title)
        layout.addWidget(description)
        row = QHBoxLayout()
        self.path = QLineEdit()
        self.path.setText(str(self.suggested_path()))
        choose = QPushButton("Choose Folder")
        choose.clicked.connect(self.choose)
        row.addWidget(self.path, 1)
        row.addWidget(choose)
        layout.addLayout(row)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Create Workspace")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def choose(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self, "Choose the Data Folder", str(self.suggested_path().parent)
        )
        if path:
            self.path.setText(path)

    @staticmethod
    def suggested_path() -> Path:
        documents = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation
        )
        return default_workspace_path(documents or None)

    def accept(self) -> None:
        raw_path = self.path.text().strip()
        if not raw_path:
            QMessageBox.warning(
                self, "Folder Required", "Choose a folder for the application data."
            )
            return
        target = Path(raw_path).expanduser()
        try:
            target = ensure_writable_directory(target)
        except OSError as exc:
            QMessageBox.critical(
                self,
                "Folder Is Not Writable",
                "Chef Pricing could not write to the selected folder.\n\n"
                f"Path: {target}\nError: {exc}\n\n"
                "Choose a folder owned by your user, another writable drive, "
                "or check the folder permissions.",
            )
            return
        self.path.setText(str(target.resolve()))
        super().accept()


def load_styles(application: QApplication) -> None:
    path = resource_path("frontend", "resources", "main.qss")
    application.setStyleSheet(path.read_text(encoding="utf-8"))


def run(workspace_path: str | Path | None = None) -> int:
    application = QApplication([sys.argv[0]])
    application.setApplicationName(PRODUCT_NAME)
    application.setOrganizationName(PUBLISHER)
    load_styles(application)
    settings = QSettings()
    workspace_path = (
        str(Path(workspace_path).expanduser().resolve())
        if workspace_path
        else settings.value("workspace_path", "", str)
    )
    while True:
        if not workspace_path or not Path(workspace_path).exists():
            welcome = WelcomeDialog()
            if welcome.exec() != QDialog.DialogCode.Accepted:
                return 0
            workspace_path = welcome.path.text().strip()
        try:
            workspace_path = str(ensure_writable_directory(workspace_path))
            app_service = ChefPricingApp(workspace_path)
            break
        except OSError as exc:
            QMessageBox.critical(
                None,
                "Workspace Unavailable",
                "Chef Pricing could not access the data folder with write "
                f"permission.\n\n{workspace_path}\n\nError: {exc}",
            )
            settings.remove("workspace_path")
            workspace_path = ""
    settings.setValue("workspace_path", workspace_path)
    if app_service.workspace.settings().get("backup_on_startup") == "true":
        app_service.workspace.backup()
    window = MainWindow(app_service)
    window.show()
    return application.exec()
