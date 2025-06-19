# 用户指南

欢迎使用 MkDocs Material i18n 插件！

## 功能介绍

本插件为 MkDocs Material 主题提供了强大的国际化支持，包括：

- 多语言站点支持
- 自动语言检测
- 独立导航配置
- 语言切换功能

## 基本配置

在 `mkdocs.yml` 中配置插件：

```yaml
plugins:
  - i18n:
      locales:
        - name: 中文
          link: /zh/
          lang: zh
        - name: English
          link: /en/
          lang: en
```

## 高级功能

### 独立导航

每种语言可以配置独立的导航结构：

```yaml
plugins:
  - i18n:
      locales:
        - name: 中文
          link: /zh/
          lang: zh
          nav:
            - 首页: index.md
            - 用户指南: guide.md
            - 开发文档: docs.md
```

这样可以为不同语言提供完全不同的内容组织方式。
