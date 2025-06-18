"""MkDocs Material i18n Plugin"""

from mkdocs.plugins import BasePlugin


class MaterialI18nPlugin(BasePlugin):
    """MkDocs Material i18n Plugin"""
    
    def on_config(self, config, **kwargs):
        """Called when the config is loaded"""
        return config