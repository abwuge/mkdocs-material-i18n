"""MkDocs Material i18n Plugin"""

from mkdocs.plugins import BasePlugin, get_plugin_logger
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page
from mkdocs.structure.nav import Navigation

from .config import MaterialI18nPluginConfig
from .index import IndexPageGenerator
from .language import LanguageContextManager

log = get_plugin_logger(__name__)


class MaterialI18nPlugin(BasePlugin[MaterialI18nPluginConfig]):
    """MkDocs Material i18n Plugin that enhances i18n support for MkDocs Material"""

    def __init__(self):
        super().__init__()
        self.language_manager = None

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        """Called when the config is loaded"""

        # Process locales configuration
        config = self.config.process_locales_config(config)

        if self.config.locales:
            self.language_manager = LanguageContextManager(self.config.locales)
            log.debug(
                f"Automatically configured {len(self.config.locales)} language options for Material theme"
            )

        return config

    def on_page_context(self, context: dict, page: Page, config: MkDocsConfig, nav: Navigation) -> dict:
        """Called when the page context is created, allowing modification of template variables"""
        
        if not self.language_manager:
            return context
            
        return self.language_manager.modify_page_context(context, page, config)

    def on_post_build(self, config: MkDocsConfig, **kwargs):
        """Called after the build process is complete"""
        if not self.config.locales:
            return
        
        # Create index page generator
        index_generator = IndexPageGenerator(self.config.locales, self.config.default_locale)
        
        # Generate and create the index.html file
        index_generator.create_index_file(config)
