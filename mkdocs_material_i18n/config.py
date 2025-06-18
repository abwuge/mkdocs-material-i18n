"""Configuration classes for MkDocs Material i18n Plugin"""

from mkdocs.config import base, config_options
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.config.base import ValidationError


class LocaleConfig(base.Config):
    """Configuration for a single locale"""
    name = config_options.Type(str, default='')
    link = config_options.Type(str, default='') 
    lang = config_options.Type(str, default='')
    
    def validate(self):
        """Validate locale configuration and set defaults"""
        # Call parent validation first
        errors, warnings = super().validate()
        
        # lang is required
        if not self.lang:
            errors.append(ValidationError("lang is required for each locale"))
        else:
            # Set default link if not provided
            if not self.link:
                self.link = f"/{self.lang}/"
            
            # Set default name if not provided
            if not self.name:
                self.name = self.lang
                
        return errors, warnings


class MaterialI18nPluginConfig(base.Config):
    """Configuration schema for Material i18n Plugin"""
    locales = config_options.ListOfItems(config_options.SubConfig(LocaleConfig), default=[])
    
    def process_locales_config(self, config: MkDocsConfig) -> MkDocsConfig:
        """Process locales configuration and set Material theme's alternate config"""
        
        # If plugin has locales configured, automatically set Material theme's alternate config
        if self.locales:
            # Ensure extra config exists
            if "extra" not in config:
                config["extra"] = {}

            # Convert plugin's locales config to Material theme's alternate config
            alternate_configs = []
            for locale in self.locales:
                alternate_configs.append({
                    "name": locale.name,
                    "link": locale.link,
                    "lang": locale.lang,
                })

            # Set alternate config
            config["extra"]["alternate"] = alternate_configs

        return config
