"""Tests for basic configuration functionality in MkDocs Material i18n Plugin"""

from mkdocs_material_i18n.plugin import MaterialI18nPlugin


def test_single_locale_warning():
    """Test that warning is shown when only one locale is configured"""
    from mkdocs_material_i18n.config import MaterialI18nPluginConfig

    plugin_config = MaterialI18nPluginConfig()

    # Load single locale config
    plugin_config.load_dict({"locales": [{"lang": "en"}]})

    errors, warnings = plugin_config.validate()

    # Should have no errors
    assert len(errors) == 0
    # Should have warning about less than 2 locales
    assert len(warnings) == 1
    assert "less than 2 locales" in warnings[0]


def test_empty_locales_warning():
    """Test that warning is shown when no locales are configured"""
    from mkdocs_material_i18n.config import MaterialI18nPluginConfig

    plugin_config = MaterialI18nPluginConfig()
    plugin_config.locales = []  # Empty locales

    errors, warnings = plugin_config.validate()

    # Should have no errors
    assert len(errors) == 0
    # Should have warning about less than 2 locales
    assert len(warnings) == 1
    assert "less than 2 locales" in warnings[0]


def test_no_warning_with_multiple_locales():
    """Test that no warning is shown when multiple locales are configured"""
    from mkdocs_material_i18n.config import MaterialI18nPluginConfig

    plugin_config = MaterialI18nPluginConfig()

    # Load multiple locale configs
    plugin_config.load_dict(
        {"locales": [{"lang": "en"}, {"lang": "zh"}, {"lang": "fr"}]}
    )

    errors, warnings = plugin_config.validate()

    # Should have no errors or warnings
    assert len(errors) == 0
    assert len(warnings) == 0


def test_plugin_basic_functionality():
    """Test basic plugin functionality without warnings"""
    plugin = MaterialI18nPlugin()

    # Load config with multiple locales
    plugin.load_config(
        {
            "locales": [
                {"lang": "en", "name": "English"},
                {"lang": "zh", "name": "中文"},
            ]
        }
    )

    # Test plugin functionality
    config = {}
    result_config = plugin.on_config(config)

    # Verify that alternate configuration was added
    assert "extra" in result_config
    assert "alternate" in result_config["extra"]
    assert len(result_config["extra"]["alternate"]) == 2


def test_plugin_config_validation():
    """Test that plugin configuration validation works correctly"""
    from mkdocs_material_i18n.config import MaterialI18nPluginConfig

    plugin_config = MaterialI18nPluginConfig()

    # Test with valid configuration
    plugin_config.locales = []
    plugin_config.default_locale = ""

    errors, warnings = plugin_config.validate()

    # Should have no errors but should have warning
    assert len(errors) == 0
    assert len(warnings) == 1
