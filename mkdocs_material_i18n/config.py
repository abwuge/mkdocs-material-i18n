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
            errors.append(("locales", "lang is required for each locale"))
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

    default_lang = config_options.Type(str, default="")
    default_locale = config_options.SubConfig(LocaleConfig, validate=False)
    locales = config_options.ListOfItems(
        config_options.SubConfig(LocaleConfig), default=[]
    )

    def validate(self):
        """Validate plugin configuration and set defaults"""
        # Call parent validation first
        errors, warnings = super().validate()

        # Validate locales count
        if not self.locales:
            errors.append(("locales", "At least 1 locale must be configured"))
            return errors, warnings
        elif len(self.locales) == 1:
            warnings.append(
                (
                    "locales",
                    "You have only 1 locale configured. This plugin is designed for multi-language sites and may not be necessary for single-language sites.",
                )
            )

        # Set default_lang if not provided
        if not self.default_lang and not self.default_locale.lang:
            self.default_lang = self.locales[0].lang

        errors.extend(self._validate_default_locale())

        return errors, warnings

    def _validate_default_locale(self):
        """Validate default_locale configuration and set defaults if needed"""
        errors = []

        # Find the locale that matches default_lang
        matching_locale = self._find_locale_by_lang(self.default_lang)

        if not matching_locale:
            errors.append(
                (
                    "default_locale",
                    f"Default locale '{self.default_lang}' does not match any configured locale's lang",
                )
            )
            return errors

        # Handle default_locale configuration
        if not self.default_locale.lang:
            self.default_locale = matching_locale
        elif self.default_locale != matching_locale:
            errors.append(
                (
                    "default_locale",
                    "Default locale does not match configured default_lang related locale",
                )
            )

        return errors

    def _find_locale_by_lang(self, lang):
        """Find a locale by its lang attribute"""
        for locale in self.locales:
            if locale.lang == lang:
                return locale
        return None

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
