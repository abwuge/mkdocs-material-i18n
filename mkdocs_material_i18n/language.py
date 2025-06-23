"""Language detection and context management for MkDocs Material i18n Plugin"""

from mkdocs.structure.pages import Page
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import get_plugin_logger

from .locale_mapper import get_locale_mapper

log = get_plugin_logger(__name__)


class LanguageManager:
    """Manages language detection and context modification for pages"""

    def __init__(self, locales):
        """
        Initialize the language context manager

        Args:
            locales: List of locale configurations from plugin config
        """
        self.locales = locales
        self.locale_mapper = get_locale_mapper()

    def detect_page_language(self, page: Page) -> str:
        """
        Detect the language of a page based on its file path

        Args:
            page: MkDocs Page instance

        Returns:
            Language code string or None if not detected
        """

        return self.locale_mapper.detect_lang_from_path(page.file.src_path)

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

        # Get the current page's locale configuration directly
        current_locale = self.locale_mapper.detect_locale_from_path(page.file.src_path)
        if current_locale:
            # Directly modify the config theme language for this page
            config.theme.language = current_locale.lang

            # Set the localized site_name if configured
            if current_locale.site_name:
                config.site_name = current_locale.site_name
                log.debug(
                    f"Set site_name to '{current_locale.site_name}' for language '{current_locale.lang}'"
                )

            current_url = page.url
            url_parts = current_url.strip("/").split("/")
            if len(url_parts) > 1:
                path_without_lang = "/".join(url_parts[1:]) + "/"
            else:
                path_without_lang = ""
            for alt in config.extra["alternate"]:
                alt["link"] = "/" + alt["link"].split("/")[1] + "/" + path_without_lang
                log.debug(
                    f"Set language '{current_locale.lang}' for page: {page.file.src_path}"
                )

        return context
