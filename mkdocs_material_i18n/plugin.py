"""MkDocs Material i18n Plugin"""

from mkdocs.plugins import BasePlugin, get_plugin_logger
from mkdocs.config.defaults import MkDocsConfig

from .config import MaterialI18nPluginConfig

log = get_plugin_logger(__name__)


class MaterialI18nPlugin(BasePlugin[MaterialI18nPluginConfig]):
    """MkDocs Material i18n Plugin that enhances i18n support for MkDocs Material"""

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        """Called when the config is loaded"""
        
        # Process locales configuration
        config = self.config.process_locales_config(config)
        
        # Log debug information if locales are configured
        if self.config.locales:
            log.debug(
                f"Automatically configured {len(self.config.locales)} language options for Material theme"
            )
        
        return config
