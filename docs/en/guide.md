# User Guide

Welcome to MkDocs Material i18n Plugin!

## Features

This plugin provides powerful internationalization support for MkDocs Material theme, including:

- Multi-language site support
- Automatic language detection
- Independent navigation configuration
- Language switching functionality

## Basic Configuration

Configure the plugin in `mkdocs.yml`:

```yaml
plugins:
  - i18n:
      locales:
        - name: English
          link: /en/
          lang: en
        - name: 中文
          link: /zh/
          lang: zh
```

## Advanced Features

### Independent Navigation

Each language can have its own navigation structure:

```yaml
plugins:
  - i18n:
      locales:
        - name: English
          link: /en/
          lang: en
          nav:
            - Home: index.md
            - Guide: guide.md
            - API Reference: api.md
```

This allows you to provide completely different content organization for different languages.
