from pathlib import Path

import chef_pricing
from chef_pricing.frontend.main_window import money
from chef_pricing.product import default_workspace_path, resource_path


def test_stylesheet_resource_exists():
    assert resource_path("frontend", "resources", "main.qss").is_file()


def test_default_workspace_is_in_user_documents():
    path = default_workspace_path()
    assert path.name == "ChefPricingData"
    assert path.parent == Path.home() / "Documents"


def test_money_uses_dollar_symbol_and_english_number_format():
    from decimal import Decimal

    assert money(Decimal("1234.56")) == "$1,234.56"


def test_version_is_the_packaging_source_of_truth():
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
    assert 'dynamic = ["version"]' in pyproject
    assert 'version = {attr = "chef_pricing.__version__"}' in pyproject
    assert chef_pricing.__version__ == "0.1.0"


def test_inno_installer_is_per_user_and_preserves_workspace():
    installer = Path("packaging/windows/chef_pricing.iss").read_text(
        encoding="utf-8"
    )
    assert "PrivilegesRequired=lowest" in installer
    assert r"DefaultDirName={localappdata}\Programs\Chef Pricing" in installer
    assert "ArchitecturesAllowed=x64compatible" in installer
    assert "MinVersion=10.0.10240" in installer
    assert "desktopicon" in installer
    assert "[UninstallDelete]" not in installer
    assert "ChefPricingData" not in installer
    assert 'Name: "english"' in installer


def test_new_workspace_defaults_to_aud(tmp_path):
    from chef_pricing.application.app_service import ChefPricingApp

    app = ChefPricingApp(tmp_path)
    assert app.workspace.settings()["currency"] == "AUD"
