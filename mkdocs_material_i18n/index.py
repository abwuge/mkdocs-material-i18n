"""Index page generation functionality for MkDocs Material i18n Plugin"""

import os
from typing import List, Optional
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import get_plugin_logger

from .config import LocaleConfig

log = get_plugin_logger(__name__)


# Default index.html template for language redirection
DEFAULT_INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>Redirecting ...</title>

    <!-- Redirect to {default_locale_lang} after 3s (Which usually happens when JavaScript is disabled) -->
    <meta http-equiv="refresh" content="3;url={default_locale_link}" />
  </head>
  <body>
    <script>
      (function () {{
        const LANGUAGE_MAP = {language_map};

        const DEFAULT_LANGUAGE = "{default_locale_link}";

        const userLang = (
          navigator.language ||
          navigator.userLanguage ||
          navigator.browserLanguage
        ).toLowerCase();

        window.location.href =
          LANGUAGE_MAP[userLang] ||
          LANGUAGE_MAP[userLang.split("-")[0]] ||
          DEFAULT_LANGUAGE;
      }})();
    </script>
  </body>
</html>"""


class IndexPageGenerator:
    """Handles generation of the root index.html page for multi-language sites"""

    def __init__(self, locales: List[LocaleConfig], default_locale: LocaleConfig):
        """Initialize the index page generator

        Args:
            locales: List of configured locales
            default_locale: Default locale configuration
        """
        self.locales = locales
        self.default_locale = default_locale

    def generate_language_map(self) -> str:
        """Generate JavaScript language map for the redirect script

        Returns:
            Formatted JavaScript object string for language mapping
        """

        # Collect all language mappings
        language_map = {}
        for locale in self.locales:
            lang_code = locale.lang.lower()
            language_map[lang_code] = locale.link

        # Add missing base language mappings
        for lang_code, link in list(language_map.items()):
            if "-" in lang_code:
                base_lang = lang_code.split("-")[0]
                if base_lang not in language_map:
                    language_map[base_lang] = link

        # Convert to JavaScript object format
        language_map_items = [
            f'"{lang_code}": "{link}"' for lang_code, link in language_map.items()
        ]

        return (
            "{\n          " + ",\n          ".join(language_map_items) + "\n        }"
        )

    def generate_default_index_html(self) -> str:
        """Generate the default index.html content with language redirection

        Returns:
            Complete HTML content as string
        """
        language_map = self.generate_language_map()

        return DEFAULT_INDEX_TEMPLATE.format(
            default_locale_lang=self.default_locale.lang,
            default_locale_link=self.default_locale.link,
            language_map=language_map,
        )

    def get_custom_index_template(self, config: MkDocsConfig) -> Optional[str]:
        """Check if user has provided a custom index.html template via theme override

        Args:
            config: MkDocs configuration object

        Returns:
            Custom template content if found, None otherwise
        """
        # Check for custom index.html in theme's custom_dir
        if config.theme.custom_dir:
            custom_index_path = os.path.join(config.theme.custom_dir, "index.html")
            if os.path.exists(custom_index_path):
                try:
                    with open(custom_index_path, "r", encoding="utf-8") as f:
                        return f.read()
                except Exception as e:
                    log.warning(f"Failed to read custom index.html template: {e}")

        return None

    def create_index_file(self, config: MkDocsConfig) -> bool:
        """Create the index.html file in the site directory

        Args:
            config: MkDocs configuration object

        Returns:
            True if file was created successfully, False otherwise
        """
        # Check for custom template first
        custom_template = self.get_custom_index_template(config)

        if custom_template:
            html_content = custom_template
            log.info("Using custom index.html template from theme override")
        else:
            # Generate default template with language redirection
            html_content = self.generate_default_index_html()
            log.info("Generated default index.html with language redirection")

        if not html_content:
            log.warning("No HTML content generated for index.html")
            return False

        # Write index.html to site directory
        index_path = os.path.join(config.site_dir, "index.html")
        try:
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            log.debug(f"Created index.html at {index_path}")
            return True
        except Exception as e:
            log.error(f"Failed to create index.html: {e}")
            return False
