"""Tests for default_locale functionality in MkDocs Material i18n Plugin"""

from mkdocs_material_i18n.plugin import MaterialI18nPlugin


def test_default_locale_auto_set():
    """Test that default_locale is automatically set to first locale's lang"""
    from mkdocs_material_i18n.config import MaterialI18nPluginConfig

    plugin_config = MaterialI18nPluginConfig()

    # Load locale configs using dictionary format
    plugin_config.load_dict({"locales": [{"lang": "en"}, {"lang": "zh"}]})
    # default_locale not provided

    errors, warnings = plugin_config.validate()

    # Should have no errors
    assert len(errors) == 0
    # default_locale should be set to first locale's lang
    assert plugin_config.default_locale == "en"


def test_default_locale_provided():
    """Test that provided default_locale is not overridden"""
    from mkdocs_material_i18n.config import MaterialI18nPluginConfig

    plugin_config = MaterialI18nPluginConfig()

    # Load locale configs using dictionary format
    plugin_config.load_dict(
        {
            "locales": [{"lang": "en"}, {"lang": "zh"}],
            "default_locale": "zh",  # Explicitly set to second locale
        }
    )

    errors, warnings = plugin_config.validate()

    # Should have no errors
    assert len(errors) == 0
    # default_locale should remain as provided
    assert plugin_config.default_locale == "zh"


def test_default_locale_empty_locales():
    """Test that default_locale remains empty when no locales are provided"""
    from mkdocs_material_i18n.config import MaterialI18nPluginConfig

    plugin_config = MaterialI18nPluginConfig()
    plugin_config.locales = []  # Empty locales
    # default_locale not provided

    errors, warnings = plugin_config.validate()

    # Should have no errors
    assert len(errors) == 0
    # default_locale should remain empty
    assert plugin_config.default_locale == ""


def test_plugin_with_default_locale():
    """Test plugin integration with default_locale functionality"""
    plugin = MaterialI18nPlugin()

    # Load config with locales
    plugin.load_config(
        {
            "locales": [
                {"lang": "en"},
                {"lang": "zh", "name": "中文"},
            ]
            # default_locale not provided, should auto-set to "en"
        }
    )

    # Check that default_locale was set automatically
    assert plugin.config.default_locale == "en"

    # Test plugin functionality still works
    config = {}
    result_config = plugin.on_config(config)

    # Verify that alternate configuration was added
    assert "extra" in result_config
    assert "alternate" in result_config["extra"]
    assert len(result_config["extra"]["alternate"]) == 2


def test_plugin_with_explicit_default_locale():
    """Test plugin with explicitly set default_locale"""
    plugin = MaterialI18nPlugin()

    # Load config with explicit default_locale
    plugin.load_config(
        {
            "locales": [
                {"lang": "en"},
                {"lang": "zh", "name": "中文"},
                {"lang": "fr", "name": "Français"},
            ],
            "default_locale": "fr",  # Explicitly set to French
        }
    )

    # Check that default_locale was set as specified
    assert plugin.config.default_locale == "fr"

    # Test plugin functionality still works
    config = {}
    result_config = plugin.on_config(config)

    # Verify that alternate configuration was added
    assert "extra" in result_config
    assert "alternate" in result_config["extra"]
    assert len(result_config["extra"]["alternate"]) == 3
