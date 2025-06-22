"""Tests for default_lang and default_locale functionality in MkDocs Material i18n Plugin"""

from mkdocs.config import load_config
from mkdocs_material_i18n.config import MaterialI18nPluginConfig


def test_default_lang_auto_set():
    """Test that default_lang is automatically set to first locale's lang"""
    # Load config using load_config
    config = load_config("tests/mkdocs.yml")

    # Get plugin config
    plugin_config = config["plugins"]["i18n"].config

    # default_lang should be set to first locale's lang
    assert plugin_config.default_lang == "en"


def test_plugin_with_default_lang():
    """Test plugin integration with default_lang functionality"""
    # Load config with locales (default_lang should auto-set to "en")
    config = load_config(
        "tests/mkdocs.yml",
        plugins={
            "i18n": {
                "locales": [
                    {"lang": "en"},
                    {"lang": "zh", "name": "中文"},
                ]
                # default_lang not provided, should auto-set to "en"
            },
        },
    )

    plugin = config["plugins"]["i18n"]

    # Check that default_lang was set automatically
    assert plugin.config.default_lang == "en"


def test_plugin_with_explicit_default_lang():
    """Test plugin with explicitly set default_lang"""
    # Load config with explicit default_lang
    config = load_config(
        "tests/mkdocs.yml",
        plugins={
            "i18n": {
                "locales": [
                    {"lang": "en"},
                    {"lang": "zh", "name": "中文"},
                    {"lang": "fr", "name": "Français"},
                ],
                "default_lang": "fr",  # Explicitly set to French
            },
        },
    )

    plugin = config["plugins"]["i18n"]

    # Check that default_lang was set as specified
    assert plugin.config.default_lang == "fr"


def test_default_locale_auto_set():
    """Test that default_locale is automatically set to matching locale"""
    config = load_config(
        "tests/mkdocs.yml",
        plugins={
            "i18n": {
                "locales": [
                    {"lang": "en", "name": "English"},
                    {"lang": "zh", "name": "中文"},
                ],
                "default_lang": "zh",  # Explicitly set to Chinese
            },
        },
    )

    plugin = config["plugins"]["i18n"]
    plugin_config = plugin.config

    # default_locale should be set to the matching locale
    assert plugin_config.default_locale is not None
    assert plugin_config.default_locale.lang == "zh"
    assert plugin_config.default_locale.name == "中文"


def test_default_locale_lang_mismatch_error_1():
    """Test error when default_locale.lang doesn't match default_lang"""
    plugin_config = MaterialI18nPluginConfig()
    plugin_config.load_dict(
        {
            "locales": [
                {"lang": "en", "name": "English"},
                {"lang": "zh", "name": "中文"},
            ],
            "default_lang": "en",
            "default_locale": {
                "lang": "en",
                "name": "English (Custom)",
                "link": "/en-custom/",
            },
        }
    )

    errors, warnings = plugin_config.validate()

    # Should have error for mismatched default_locale
    assert len(errors) == 1
    assert (
        "Default locale does not match configured default_lang related locale"
        in str(errors[0])
    )


def test_default_locale_lang_mismatch_error_2():
    """Test error when default_locale.lang doesn't match default_lang"""
    plugin_config = MaterialI18nPluginConfig()
    plugin_config.load_dict(
        {
            "locales": [
                {"lang": "en", "name": "English"},
                {"lang": "zh", "name": "中文"},
            ],
            "default_lang": "en",
            "default_locale": {
                "lang": "zh",  # Mismatched lang
                "name": "Chinese",
            },
        }
    )

    errors, warnings = plugin_config.validate()

    # Should have error for mismatched lang
    assert len(errors) == 1
    assert (
        "Default locale does not match configured default_lang related locale"
        in str(errors[0])
    )


def test_default_lang_not_in_locales_error():
    """Test error when default_lang doesn't match any locale"""
    plugin_config = MaterialI18nPluginConfig()
    plugin_config.load_dict(
        {
            "locales": [
                {"lang": "en", "name": "English"},
                {"lang": "zh", "name": "中文"},
            ],
            "default_lang": "fr",  # Not in locales
        }
    )

    errors, warnings = plugin_config.validate()

    # Should have error for default_lang not matching any locale
    assert len(errors) == 1
    assert "does not match any configured locale's lang" in str(errors[0])
