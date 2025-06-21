"""MkDocs Material i18n Plugin"""

from mkdocs.plugins import BasePlugin, get_plugin_logger
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page
from mkdocs.structure.nav import Navigation

from .config import MaterialI18nPluginConfig
from .index import IndexPageGenerator
from .language import LanguageContextManager
from .navigation import NavigationManager

log = get_plugin_logger(__name__)


class MaterialI18nPlugin(BasePlugin[MaterialI18nPluginConfig]):
    """MkDocs Material i18n Plugin that enhances i18n support for MkDocs Material"""

    def __init__(self):
        super().__init__()
        self.language_manager = None
        self.navigation_manager = None

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        """Called when the config is loaded"""

        # Process locales configuration
        config = self.config.process_locales_config(config)

        if self.config.locales:
            self.language_manager = LanguageContextManager(self.config.locales)
            self.navigation_manager = NavigationManager(self.config.locales)
            log.debug(
                f"Automatically configured {len(self.config.locales)} language options for Material theme"
            )

        return config

    def on_nav(self, nav: Navigation, config: MkDocsConfig, files) -> Navigation:
        """Called when the navigation is created, build language-specific navigations"""

        if self.navigation_manager:
            # Build navigation structures for each language
            self.navigation_manager.build_language_navigations(nav, files, config)
            log.debug("Built language-specific navigations")

        return nav

    def on_page_context(
        self, context: dict, page: Page, config: MkDocsConfig, nav: Navigation
    ) -> dict:
        """Called when the page context is created, allowing modification of template variables"""

        # Set page language first
        if self.language_manager:
            context = self.language_manager.modify_page_context(context, page, config)

        # Modify navigation based on page language
        if self.navigation_manager:
            context = self.navigation_manager.modify_navigation_context(context, page)

        return context

    def on_post_build(self, config: MkDocsConfig, **kwargs):
        """Called after the build process is complete"""
        if not self.config.locales:
            return

        # Create index page generator
        index_generator = IndexPageGenerator(
            self.config.locales, self.config.default_locale
        )

        # Generate and create the index.html file
        index_generator.create_index_file(config)
