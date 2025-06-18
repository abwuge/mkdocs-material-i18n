"""Tests for MkDocs Material i18n Plugin"""

from mkdocs.config import load_config


def test_plugin_with_locales():
    """Test that locales configuration is converted to alternate configuration"""
    # Load config with specific locales
    config = load_config(
        "tests/mkdocs.yml",
        plugins={
            "i18n": {
                "locales": [
                    {"name": "中文", "link": "/zh/", "lang": "zh"},
                    {"name": "English", "link": "/en/", "lang": "en"},
                ]
            },
        },
    )

    plugin = config["plugins"]["i18n"]

    # Call the method
    result_config = plugin.on_config(config)

    # Verify that alternate configuration was added
    assert "extra" in result_config
    assert "alternate" in result_config["extra"]

    alternate = result_config["extra"]["alternate"]
    assert len(alternate) == 2

    # Verify first locale
    assert alternate[0]["name"] == "中文"
    assert alternate[0]["link"] == "/zh/"
    assert alternate[0]["lang"] == "zh"

    # Verify second locale
    assert alternate[1]["name"] == "English"
    assert alternate[1]["link"] == "/en/"
    assert alternate[1]["lang"] == "en"


def test_plugin_without_locales():
    """Test that config is unchanged when no locales are configured"""
    # Load config with empty locales
    config = load_config(
        "tests/mkdocs.yml",
        plugins={
            "i18n": {"locales": []},
        },
    )

    plugin = config["plugins"]["i18n"]

    # Call the method
    original_config = config.copy()
    result_config = plugin.on_config(config)

    # Verify that config is unchanged
    assert result_config == original_config


def test_plugin_preserves_existing_extra():
    """Test that existing extra configuration is preserved"""
    # Load config with single locale
    config = load_config(
        "tests/mkdocs.yml",
        plugins={
            "i18n": {"locales": [{"name": "English", "link": "/en/", "lang": "en"}]},
        },
        extra={
            "social": [
                {
                    "icon": "fontawesome/brands/github",
                    "link": "https://github.com/example",
                }
            ]
        },
    )

    plugin = config["plugins"]["i18n"]

    # Call the method
    result_config = plugin.on_config(config)

    # Verify that existing extra config is preserved
    assert "social" in result_config["extra"]
    assert "alternate" in result_config["extra"]


def test_locale_validation_lang_required():
    """Test that lang field is required for each locale"""
    from mkdocs_material_i18n.config import LocaleConfig
    from mkdocs.config.base import ValidationError

    locale_config = LocaleConfig()
    locale_config.name = "English"
    locale_config.link = "/en/"
    # Missing lang field

    errors, warnings = locale_config.validate()

    # Should have validation error for missing lang
    assert len(errors) == 1
    assert isinstance(errors[0], ValidationError)
    assert "lang is required" in str(errors[0])


def test_locale_validation_default_link():
    """Test that link defaults to /{lang}/ when not provided"""
    from mkdocs_material_i18n.config import LocaleConfig

    locale_config = LocaleConfig()
    locale_config.lang = "zh"
    # link not provided

    errors, warnings = locale_config.validate()

    # Should have no errors
    assert len(errors) == 0
    # Link should be set to default
    assert locale_config.link == "/zh/"


def test_locale_validation_default_name():
    """Test that name defaults to lang when not provided"""
    from mkdocs_material_i18n.config import LocaleConfig

    locale_config = LocaleConfig()
    locale_config.lang = "en"
    # name not provided

    errors, warnings = locale_config.validate()

    # Should have no errors
    assert len(errors) == 0
    # Name should be set to default
    assert locale_config.name == "en"


def test_locale_validation_all_defaults():
    """Test that both link and name default properly when only lang is provided"""
    from mkdocs_material_i18n.config import LocaleConfig

    locale_config = LocaleConfig()
    locale_config.lang = "fr"
    # Both name and link not provided

    errors, warnings = locale_config.validate()

    # Should have no errors
    assert len(errors) == 0
    # Both should be set to defaults
    assert locale_config.link == "/fr/"
    assert locale_config.name == "fr"


def test_locale_validation_no_defaults_when_provided():
    """Test that provided values are not overridden"""
    from mkdocs_material_i18n.config import LocaleConfig

    locale_config = LocaleConfig()
    locale_config.lang = "zh"
    locale_config.name = "中文"
    locale_config.link = "/chinese/"

    errors, warnings = locale_config.validate()

    # Should have no errors
    assert len(errors) == 0
    # Values should remain as provided
    assert locale_config.name == "中文"
    assert locale_config.link == "/chinese/"
    assert locale_config.lang == "zh"


def test_plugin_config_validation_integration():
    """Test that plugin works with locales that use default values"""
    # Load config with minimal locale info (only lang)
    config = load_config(
        "tests/mkdocs.yml",
        plugins={
            "i18n": {
                "locales": [
                    {"lang": "en"},  # Only lang provided
                    {"lang": "zh", "name": "中文"},  # lang and name provided
                    {"lang": "fr", "link": "/french/"},  # lang and link provided
                ]
            },
        },
    )

    plugin = config["plugins"]["i18n"]

    # Call the method
    result_config = plugin.on_config(config)

    # Verify that alternate configuration was added
    assert "extra" in result_config
    assert "alternate" in result_config["extra"]

    alternate = result_config["extra"]["alternate"]
    assert len(alternate) == 3

    # Verify first locale (defaults applied)
    assert alternate[0]["name"] == "en"  # default name
    assert alternate[0]["link"] == "/en/"  # default link
    assert alternate[0]["lang"] == "en"

    # Verify second locale (name provided, link defaulted)
    assert alternate[1]["name"] == "中文"  # provided name
    assert alternate[1]["link"] == "/zh/"  # default link
    assert alternate[1]["lang"] == "zh"

    # Verify third locale (link provided, name defaulted)
    assert alternate[2]["name"] == "fr"  # default name
    assert alternate[2]["link"] == "/french/"  # provided link
    assert alternate[2]["lang"] == "fr"
