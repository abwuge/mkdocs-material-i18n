"""Configuration classes for MkDocs Material i18n Plugin"""

from mkdocs.config import base, config_options
from mkdocs.config.defaults import MkDocsConfig


class LocaleConfig(base.Config):
    """Configuration for a single locale"""

    name = config_options.Type(str, default="")
    link = config_options.Type(str, default="")
    lang = config_options.Type(str, default="")

    def validate(self):
        """Validate locale configuration and set defaults"""
        # Call parent validation first
        errors, warnings = super().validate()

        # lang is required
        if not self.lang:
            errors.append("lang is required for each locale")
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

    default_locale = config_options.Type(str, default="")
    locales = config_options.ListOfItems(
        config_options.SubConfig(LocaleConfig), default=[]
    )

    def validate(self):
        """Validate plugin configuration and set defaults"""
        # Call parent validation first
        errors, warnings = super().validate()

        locales_count = len(self.locales)
        # Error if no locales configured
        if locales_count == 0:
            errors.append("At least 1 locale must be configured")
        # Warn if only one locale configured
        elif locales_count == 1:
            warnings.append(
                "You have only 1 locale configured. This plugin is designed for multi-language sites and may not be necessary for single-language sites."
            )

        # Set default_locale to first locale's lang if not provided
        if not self.default_locale and self.locales:
            self.default_locale = self.locales[0].lang

        return errors, warnings

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
                alternate_configs.append(
                    {
                        "name": locale.name,
                        "link": locale.link,
                        "lang": locale.lang,
                    }
                )

            # Set alternate config
            config["extra"]["alternate"] = alternate_configs

        return config
