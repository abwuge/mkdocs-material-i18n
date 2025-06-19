# API Reference

API reference documentation for MkDocs Material i18n Plugin.

## Plugin Configuration

### MaterialI18nPluginConfig

Main configuration class that defines plugin configuration options.

#### Configuration Options

- `default_lang`: Default language code
- `locales`: List of locale configurations

### LocaleConfig

Configuration class for individual language settings.

#### Configuration Options

- `name`: Display name for the language
- `link`: URL path for the language
- `lang`: Language code
- `nav`: Navigation configuration (optional)

## Hook Functions

### on_config

Called when configuration is loaded, used to process language configurations.

### on_nav

Called when navigation is built, used to apply language-specific navigation.

### on_page_context

Called when page context is created, used to set page language.

## Example Code

```python
from mkdocs_material_i18n import MaterialI18nPlugin

# Plugin automatically handles multi-language configuration
plugin = MaterialI18nPlugin()
```
