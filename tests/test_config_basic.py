"""Tests for basic configuration functionality in MkDocs Material i18n Plugin"""

from mkdocs_material_i18n.config import MaterialI18nPluginConfig


def test_empty_locales_error():
    """Test that error is shown when no locales are configured"""
    plugin_config = MaterialI18nPluginConfig()
    plugin_config.locales = []  # Empty locales

    errors, warnings = plugin_config.validate()
    # Should have error for no locales configured
    assert len(errors) == 1
    assert len(warnings) == 0
    assert "At least 1 locale must be configured" in str(errors[0])


def test_single_locale_warning():
    """Test that warning is shown when only one locale is configured"""

    plugin_config = MaterialI18nPluginConfig()
    plugin_config.load_dict({"locales": [{"lang": "en"}]})
    errors, warnings = plugin_config.validate()

    # Should have no errors but warning about only 1 locale
    assert len(errors) == 0
    assert len(warnings) == 1
    assert "only 1 locale configured" in warnings[0]


def test_no_warning_with_multiple_locales():
    """Test that no warning is shown when multiple locales are configured"""
    # Test the plugin validation behavior directly

    plugin_config = MaterialI18nPluginConfig()
    plugin_config.load_dict(
        {"locales": [{"lang": "en"}, {"lang": "zh"}, {"lang": "fr"}]}
    )
    errors, warnings = plugin_config.validate()

    # Should have no errors or warnings
    assert len(errors) == 0
    assert len(warnings) == 0
