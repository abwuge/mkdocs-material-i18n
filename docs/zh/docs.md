# API 文档

MkDocs Material i18n 插件 API 参考文档。

## 插件配置

### MaterialI18nPluginConfig

主要配置类，用于定义插件的配置选项。

#### 配置选项

- `default_lang`: 默认语言代码
- `locales`: 语言列表配置

### LocaleConfig

单个语言的配置类。

#### 配置选项

- `name`: 语言显示名称
- `link`: 语言链接路径
- `lang`: 语言代码
- `nav`: 导航配置（可选）

## 钩子函数

### on_config

在配置加载时调用，用于处理语言配置。

### on_nav

在导航构建时调用，用于应用语言特定的导航。

### on_page_context

在页面上下文创建时调用，用于设置页面语言。

## 示例代码

```python
from mkdocs_material_i18n import MaterialI18nPlugin

# 插件会自动处理多语言配置
plugin = MaterialI18nPlugin()
```
