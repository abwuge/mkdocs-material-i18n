"""Tests for default_locale functionality in MkDocs Material i18n Plugin"""

from mkdocs.config import load_config


def test_default_locale_auto_set():
    """Test that default_locale is automatically set to first locale's lang"""
    # Load config using load_config
    config = load_config("tests/mkdocs.yml")

    # Get plugin config
    plugin_config = config["plugins"]["i18n"].config

    # default_locale should be set to first locale's lang
    assert plugin_config.default_locale == "en"


def test_default_locale_empty_locales():
    """Test that default_locale remains empty when no locales are provided"""
    # Load config with empty locales
    config = load_config(
        "tests/mkdocs.yml",
        plugins={
            "i18n": {
                "locales": [],  # Empty locales
            },
        },
    )

    # Get plugin config
    plugin_config = config["plugins"]["i18n"].config

    # default_locale should remain empty
    assert plugin_config.default_locale == ""


def test_plugin_with_default_locale():
    """Test plugin integration with default_locale functionality"""
    # Load config with locales (default_locale should auto-set to "en")
    config = load_config(
        "tests/mkdocs.yml",
        plugins={
            "i18n": {
                "locales": [
                    {"lang": "en"},
                    {"lang": "zh", "name": "中文"},
                ]
                # default_locale not provided, should auto-set to "en"
            },
        },
    )

    plugin = config["plugins"]["i18n"]

    # Check that default_locale was set automatically
    assert plugin.config.default_locale == "en"


def test_plugin_with_explicit_default_locale():
    """Test plugin with explicitly set default_locale"""
    # Load config with explicit default_locale
    config = load_config(
        "tests/mkdocs.yml",
        plugins={
            "i18n": {
                "locales": [
                    {"lang": "en"},
                    {"lang": "zh", "name": "中文"},
                    {"lang": "fr", "name": "Français"},
                ],
                "default_locale": "fr",  # Explicitly set to French
            },
        },
    )

    plugin = config["plugins"]["i18n"]

    # Check that default_locale was set as specified
    assert plugin.config.default_locale == "fr"
