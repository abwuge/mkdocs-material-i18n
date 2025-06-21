"""Navigation management for MkDocs Material i18n Plugin"""

from typing import Dict, List, Optional
from mkdocs.structure.nav import Navigation, Section, Link
from mkdocs.structure.pages import Page
from mkdocs.structure.files import Files
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import get_plugin_logger

from .config import LocaleConfig

log = get_plugin_logger(__name__)


class NavigationManager:
    """Manages language-specific navigation structures"""

    def __init__(self, locales: List[LocaleConfig]):
        self.locales = locales
        self.language_navs: Dict[str, Navigation] = {}
        self.original_nav: Optional[Navigation] = None

    def build_language_navigations(self, nav: Navigation, files: Files, config: MkDocsConfig) -> None:
        """Build navigation structures for each language"""
        self.original_nav = nav
        
        # Create language-specific navigations
        for locale in self.locales:
            lang = locale.lang
            language_nav = self._build_navigation_for_language(nav, files, config, locale)
            self.language_navs[lang] = language_nav
            log.debug(f"Built navigation for language: {lang}")

    def _build_navigation_for_language(
        self, 
        original_nav: Navigation, 
        files: Files, 
        config: MkDocsConfig, 
        locale: LocaleConfig
    ) -> Navigation:
        """Build navigation for a specific language"""
        lang = locale.lang
        
        # If locale has custom nav configuration, use it
        if locale.nav:
            # Build navigation from locale's nav config
            return self._build_nav_from_config(locale.nav, files, config, lang)
        
        # Otherwise, filter original navigation by language
        filtered_items = self._filter_nav_items_by_language(original_nav.items, lang)
        filtered_pages = self._filter_pages_by_language(original_nav.pages, lang)
        
        return Navigation(filtered_items, filtered_pages)

    def _build_nav_from_config(self, nav_config, files: Files, config: MkDocsConfig, lang: str) -> Navigation:
        """Build navigation from configuration (similar to MkDocs core logic)"""
        from mkdocs.structure.nav import _data_to_navigation, _get_by_type, _add_previous_and_next_links, _add_parent_links
        
        # Convert nav config to navigation items
        items = _data_to_navigation(nav_config, files, config)
        if not isinstance(items, list):
            items = [items]
        
        # Get only the pages from the navigation
        pages = _get_by_type(items, Page)
        
        # Filter pages by language
        pages = self._filter_pages_by_language(pages, lang)
        
        # Include next, previous and parent links
        _add_previous_and_next_links(pages)
        _add_parent_links(items)
        
        return Navigation(items, pages)

    def _filter_nav_items_by_language(self, items: List, lang: str) -> List:
        """Filter navigation items by language"""
        filtered_items = []
        
        for item in items:
            if isinstance(item, Page):
                if self._page_matches_language(item, lang):
                    filtered_items.append(item)
            elif isinstance(item, Section):
                # Recursively filter section children
                filtered_children = self._filter_nav_items_by_language(item.children, lang)
                if filtered_children:
                    # Create new section with filtered children
                    new_section = Section(item.title, filtered_children)
                    new_section.active = item.active
                    filtered_items.append(new_section)
            elif isinstance(item, Link):
                # Keep all links
                filtered_items.append(item)
        
        return filtered_items

    def _filter_pages_by_language(self, pages: List[Page], lang: str) -> List[Page]:
        """Filter pages by language"""
        return [page for page in pages if self._page_matches_language(page, lang)]

    def _page_matches_language(self, page: Page, lang: str) -> bool:
        """Check if a page belongs to the specified language"""
        # Check if page URL starts with language prefix
        if page.url.startswith(f"{lang}/") or page.url.startswith(f"/{lang}/"):
            return True
        
        # Check if page file path contains language directory
        if hasattr(page.file, 'src_uri'):
            src_uri = page.file.src_uri
            if src_uri.startswith(f"{lang}/") or f"/{lang}/" in src_uri:
                return True
        
        return False

    def get_navigation_for_language(self, lang: str) -> Optional[Navigation]:
        """Get navigation for a specific language"""
        return self.language_navs.get(lang)

    def get_page_language(self, page: Page) -> Optional[str]:
        """Determine the language of a page"""
        for locale in self.locales:
            if self._page_matches_language(page, locale.lang):
                return locale.lang
        return None

    def modify_navigation_context(self, context: dict, page: Page) -> dict:
        """Modify the navigation context for a page"""
        page_lang = self.get_page_language(page)
        
        if page_lang and page_lang in self.language_navs:
            # Replace the navigation with language-specific navigation
            context["nav"] = self.language_navs[page_lang]
            log.debug(f"Set navigation for page {page.url} to language: {page_lang}")
        
        return context
