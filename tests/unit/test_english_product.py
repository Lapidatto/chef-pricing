from __future__ import annotations

import os
import re
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel, QPushButton

from chef_pricing.application.app_service import ChefPricingApp
from chef_pricing.frontend.main_window import MainWindow


PORTUGUESE_TERMS = (
    "arquivo",
    "pasta",
    "prato",
    "ingrediente",
    "producao",
    "produção",
    "preco",
    "preço",
    "custo",
    "erro",
    "aviso",
    "salvar",
    "editar",
    "validar",
    "configuracoes",
    "configurações",
    "relatorio",
    "relatório",
    "fornecedor",
    "quantidade",
    "unidade",
    "perda",
    "escolha",
    "executar",
    "instalador",
    "restaurar",
    "moeda",
    "cozinha",
)


def test_product_files_do_not_contain_portuguese_copy():
    roots = (
        Path("src/chef_pricing"),
        Path("scripts"),
        Path("packaging"),
        Path("data_templates"),
        Path("sample_workspace"),
        Path("docs"),
    )
    checked_suffixes = {".py", ".md", ".sh", ".bat", ".iss", ".csv"}
    findings = []
    for root in roots:
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in checked_suffixes:
                continue
            if "egg-info" in path.parts or "__pycache__" in path.parts:
                continue
            text = path.read_text(encoding="utf-8-sig").lower()
            for term in PORTUGUESE_TERMS:
                if re.search(rf"\b{re.escape(term)}\b", text):
                    findings.append(f"{path}: {term}")
    assert findings == []


def test_main_window_renders_english_copy(tmp_path):
    application = QApplication.instance() or QApplication([])
    window = MainWindow(ChefPricingApp(tmp_path))
    visible_copy = [
        widget.text()
        for widget in (
            window.findChildren(QLabel) + window.findChildren(QPushButton)
        )
    ]
    assert window.windowTitle() == "Chef Pricing - Costing and Pricing"
    assert "Overview" in MainWindow.NAVIGATION
    assert "Ingredients" in MainWindow.NAVIGATION
    assert "Save Settings" in visible_copy
    assert "Validate Now" in visible_copy
    window.close()
    application.processEvents()
