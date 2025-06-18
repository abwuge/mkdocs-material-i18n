"""Language detection and context management for MkDocs Material i18n Plugin"""

from pathlib import Path
from mkdocs.structure.pages import Page
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import get_plugin_logger

log = get_plugin_logger(__name__)


class LanguageContextManager:
    """Manages language detection and context modification for pages"""

    def __init__(self, locales):
        """
        Initialize the language context manager

        Args:
            locales: List of locale configurations from plugin config
        """
        self.locales = locales
        # Build link to lang mapping table for fast lookup
        self.link_to_lang = {}
        for locale in locales:
            # Extract the first level directory from link
            link_dir = locale.link.strip("/").split("/")[0]
            if link_dir:  # Only add non-empty directories
                self.link_to_lang[link_dir] = locale.lang

    def detect_page_language(self, page: Page) -> str:
        """
        Detect the language of a page based on its file path

        Args:
            page: MkDocs Page instance

        Returns:
            Language code string or None if not detected
        """
        # Get the source path of the page
        src_path = page.file.src_path

        first_dir = Path(src_path).parts[0] if Path(src_path).parts else None
        return self.link_to_lang.get(first_dir) if first_dir else None

    def modify_page_context(
        self, context: dict, page: Page, config: MkDocsConfig
    ) -> dict:
        """
        Modify the page context to set the correct language for the current page

        Args:
            context: Template context dictionary
            page: MkDocs Page instance
            config: MkDocs configuration object

        Returns:
            Modified context dictionary
        """
        # Determine the current page's language based on its file path
        current_language = self.detect_page_language(page)

        if current_language:
            # Directly modify the config theme language for this page
            config.theme.language = current_language

            log.debug(
                f"Set language '{current_language}' for page: {page.file.src_path}"
            )

        return context
