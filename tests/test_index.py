"""Tests for index page generation functionality in MkDocs Material i18n Plugin"""

import os
import tempfile
from unittest.mock import Mock, patch
from mkdocs.config.defaults import MkDocsConfig

from mkdocs_material_i18n.config import LocaleConfig
from mkdocs_material_i18n.index import IndexPageManager, DEFAULT_INDEX_TEMPLATE


def create_test_locale(name: str, link: str, lang: str) -> LocaleConfig:
    """Helper function to create a test locale configuration"""
    locale = LocaleConfig()
    locale.load_dict({"name": name, "link": link, "lang": lang})
    return locale


def test_index_page_generator_initialization():
    """Test IndexPageGenerator initialization with locales"""
    # Create test locales
    locale_en = create_test_locale("English", "/en/", "en")
    locale_zh = create_test_locale("中文", "/zh/", "zh")
    default_locale = locale_en

    # Initialize generator
    generator = IndexPageManager([locale_en, locale_zh], default_locale)

    assert generator.locales == [locale_en, locale_zh]
    assert generator.default_locale == default_locale


def test_generate_language_map_basic():
    """Test basic language map generation"""
    locale_en = create_test_locale("English", "/en/", "en")
    locale_zh = create_test_locale("中文", "/zh/", "zh")
    generator = IndexPageManager([locale_en, locale_zh], locale_en)

    language_map = generator.generate_language_map()

    # Should contain both languages
    assert '"en": "/en/"' in language_map
    assert '"zh": "/zh/"' in language_map
    # Should be formatted as JavaScript object
    assert language_map.startswith("{\n")
    assert language_map.endswith("\n        }")


def test_generate_language_map_with_hyphenated_langs():
    """Test language map generation with hyphenated language codes"""
    locale_en_us = create_test_locale("English (US)", "/en-us/", "en-US")
    locale_zh_cn = create_test_locale("简体中文", "/zh-cn/", "zh-CN")
    generator = IndexPageManager([locale_en_us, locale_zh_cn], locale_en_us)

    language_map = generator.generate_language_map()

    # Should contain both full and base language codes
    assert '"en-us": "/en-us/"' in language_map
    assert '"zh-cn": "/zh-cn/"' in language_map
    assert (
        '"en": "/en-us/"' in language_map
    )  # Base language should map to first occurrence
    assert '"zh": "/zh-cn/"' in language_map


def test_generate_language_map_base_lang_priority():
    """Test that base language mapping respects the first occurrence"""
    locale_en_us = create_test_locale("English (US)", "/en-us/", "en-US")
    locale_en_gb = create_test_locale("English (UK)", "/en-gb/", "en-GB")
    generator = IndexPageManager([locale_en_us, locale_en_gb], locale_en_us)

    language_map = generator.generate_language_map()

    # Base 'en' should map to the first occurrence (en-US)
    assert '"en": "/en-us/"' in language_map
    assert '"en-us": "/en-us/"' in language_map
    assert '"en-gb": "/en-gb/"' in language_map


def test_generate_default_index_html():
    """Test default index.html generation"""
    locale_en = create_test_locale("English", "/en/", "en")
    locale_zh = create_test_locale("中文", "/zh/", "zh")
    generator = IndexPageManager([locale_en, locale_zh], locale_en)

    html_content = generator.generate_default_index_html()

    # Should be valid HTML
    assert html_content.startswith("<!DOCTYPE html>")
    assert '<html lang="en">' in html_content
    assert "</html>" in html_content

    # Should contain language redirection JavaScript
    assert "LANGUAGE_MAP" in html_content
    assert "navigator.language" in html_content
    assert "window.location.href" in html_content

    # Should contain default locale information
    assert "/en/" in html_content  # Default locale link
    assert "en" in html_content  # Default locale lang


def test_generate_default_index_html_template_formatting():
    """Test that the generated HTML properly formats template variables"""
    locale_fr = create_test_locale("Français", "/fr/", "fr")
    locale_de = create_test_locale("Deutsch", "/de/", "de")
    generator = IndexPageManager([locale_fr, locale_de], locale_fr)

    html_content = generator.generate_default_index_html()

    # Check that placeholders are properly replaced
    assert "{default_locale_lang}" not in html_content
    assert "{default_locale_link}" not in html_content
    assert "{language_map}" not in html_content

    # Check that actual values are present
    assert 'content="3;url=/fr/"' in html_content
    assert '"fr": "/fr/"' in html_content
    assert '"de": "/de/"' in html_content


def test_get_custom_index_template_no_custom_dir():
    """Test custom template retrieval when no custom directory is configured"""
    config = Mock(spec=MkDocsConfig)
    config.theme = Mock()
    config.theme.custom_dir = None

    locale_en = create_test_locale("English", "/en/", "en")
    generator = IndexPageManager([locale_en], locale_en)

    custom_template = generator.get_custom_index_template(config)
    assert custom_template is None


def test_get_custom_index_template_no_index_file():
    """Test custom template retrieval when custom directory exists but no index.html"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config = Mock(spec=MkDocsConfig)
        config.theme = Mock()
        config.theme.custom_dir = temp_dir

        locale_en = create_test_locale("English", "/en/", "en")
        generator = IndexPageManager([locale_en], locale_en)

        custom_template = generator.get_custom_index_template(config)
        assert custom_template is None


def test_get_custom_index_template_with_custom_file():
    """Test custom template retrieval when custom index.html exists"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create custom index.html
        custom_index_path = os.path.join(temp_dir, "index.html")
        custom_content = "<html><body>Custom Index</body></html>"
        with open(custom_index_path, "w", encoding="utf-8") as f:
            f.write(custom_content)

        config = Mock(spec=MkDocsConfig)
        config.theme = Mock()
        config.theme.custom_dir = temp_dir

        locale_en = create_test_locale("English", "/en/", "en")
        generator = IndexPageManager([locale_en], locale_en)

        custom_template = generator.get_custom_index_template(config)
        assert custom_template == custom_content


@patch("mkdocs_material_i18n.index.log")
def test_get_custom_index_template_read_error(mock_log):
    """Test custom template retrieval handles file read errors gracefully"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create custom index.html with restricted permissions (simulation)
        custom_index_path = os.path.join(temp_dir, "index.html")
        with open(custom_index_path, "w", encoding="utf-8") as f:
            f.write("test content")

        config = Mock(spec=MkDocsConfig)
        config.theme = Mock()
        config.theme.custom_dir = temp_dir

        locale_en = create_test_locale("English", "/en/", "en")
        generator = IndexPageManager([locale_en], locale_en)

        # Mock open to raise an exception
        with patch("builtins.open", side_effect=IOError("Permission denied")):
            custom_template = generator.get_custom_index_template(config)
            assert custom_template is None
            mock_log.warning.assert_called_once()


def test_create_index_file_with_default_template():
    """Test creating index.html file with default template"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config = Mock(spec=MkDocsConfig)
        config.site_dir = temp_dir
        config.theme = Mock()
        config.theme.custom_dir = None

        locale_en = create_test_locale("English", "/en/", "en")
        locale_zh = create_test_locale("中文", "/zh/", "zh")
        generator = IndexPageManager([locale_en, locale_zh], locale_en)

        # Create index file
        result = generator.create_index_file(config)
        assert result is True

        # Verify file was created
        index_path = os.path.join(temp_dir, "index.html")
        assert os.path.exists(index_path)

        # Verify content
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "<!DOCTYPE html>" in content
        assert "LANGUAGE_MAP" in content
        assert "/en/" in content
        assert "/zh/" in content


def test_create_index_file_with_custom_template():
    """Test creating index.html file with custom template"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create custom theme directory and index.html
        theme_dir = os.path.join(temp_dir, "theme")
        os.makedirs(theme_dir)
        custom_content = "<html><body>Custom Index Content</body></html>"
        with open(os.path.join(theme_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(custom_content)

        # Create site directory
        site_dir = os.path.join(temp_dir, "site")
        os.makedirs(site_dir)

        config = Mock(spec=MkDocsConfig)
        config.site_dir = site_dir
        config.theme = Mock()
        config.theme.custom_dir = theme_dir

        locale_en = create_test_locale("English", "/en/", "en")
        generator = IndexPageManager([locale_en], locale_en)

        # Create index file
        result = generator.create_index_file(config)
        assert result is True

        # Verify file was created with custom content
        index_path = os.path.join(site_dir, "index.html")
        assert os.path.exists(index_path)

        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert content == custom_content


@patch("mkdocs_material_i18n.index.log")
def test_create_index_file_write_error(mock_log):
    """Test index file creation handles write errors gracefully"""
    config = Mock(spec=MkDocsConfig)
    config.site_dir = "/nonexistent/directory"
    config.theme = Mock()
    config.theme.custom_dir = None

    locale_en = create_test_locale("English", "/en/", "en")
    generator = IndexPageManager([locale_en], locale_en)

    # Attempt to create index file (should fail due to nonexistent directory)
    result = generator.create_index_file(config)
    assert result is False
    mock_log.error.assert_called_once()


@patch("mkdocs_material_i18n.index.log")
def test_create_index_file_no_content_warning(mock_log):
    """Test that warning is logged when no HTML content is generated"""
    config = Mock(spec=MkDocsConfig)
    config.site_dir = "/tmp"
    config.theme = Mock()
    config.theme.custom_dir = None

    locale_en = create_test_locale("English", "/en/", "en")
    generator = IndexPageManager([locale_en], locale_en)

    # Mock generate_default_index_html to return empty content
    with patch.object(generator, "generate_default_index_html", return_value=""):
        result = generator.create_index_file(config)
        assert result is False
        mock_log.warning.assert_called_once_with(
            "No HTML content generated for index.html"
        )


def test_default_index_template_structure():
    """Test that the default template has required structure elements"""
    # Verify the template has all necessary placeholders
    assert "{default_locale_lang}" in DEFAULT_INDEX_TEMPLATE
    assert "{default_locale_link}" in DEFAULT_INDEX_TEMPLATE
    assert "{language_map}" in DEFAULT_INDEX_TEMPLATE

    # Verify basic HTML structure
    assert "<!DOCTYPE html>" in DEFAULT_INDEX_TEMPLATE
    assert '<html lang="en">' in DEFAULT_INDEX_TEMPLATE
    assert '<meta charset="UTF-8"' in DEFAULT_INDEX_TEMPLATE
    assert '<meta http-equiv="refresh"' in DEFAULT_INDEX_TEMPLATE
    assert "<script>" in DEFAULT_INDEX_TEMPLATE
    assert "navigator.language" in DEFAULT_INDEX_TEMPLATE
    assert "window.location.href" in DEFAULT_INDEX_TEMPLATE


def test_integration_full_workflow():
    """Integration test for the complete index generation workflow"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config = Mock(spec=MkDocsConfig)
        config.site_dir = temp_dir
        config.theme = Mock()
        config.theme.custom_dir = None

        # Create multiple locales including hyphenated ones
        locales = [
            create_test_locale("English", "/en/", "en"),
            create_test_locale("中文", "/zh/", "zh"),
            create_test_locale("Français", "/fr/", "fr"),
            create_test_locale("English (US)", "/en-us/", "en-US"),
        ]
        default_locale = locales[0]

        generator = IndexPageManager(locales, default_locale)

        # Test complete workflow
        result = generator.create_index_file(config)
        assert result is True

        # Verify generated file
        index_path = os.path.join(temp_dir, "index.html")
        assert os.path.exists(index_path)

        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Verify all locales are represented
        assert '"en": "/en/"' in content
        assert '"zh": "/zh/"' in content
        assert '"fr": "/fr/"' in content
        assert '"en-us": "/en-us/"' in content

        # Verify default locale is correctly set
        assert 'content="3;url=/en/"' in content

        # Verify JavaScript functionality
        assert "LANGUAGE_MAP" in content
        assert "DEFAULT_LANGUAGE" in content
        assert "navigator.language" in content
        assert "window.location.href" in content
