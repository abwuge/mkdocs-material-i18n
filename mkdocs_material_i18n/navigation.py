"""Navigation management for MkDocs Material i18n Plugin"""

from typing import Dict, List, Optional
from mkdocs.structure.nav import Navigation, get_navigation
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import get_plugin_logger

from .config import LocaleConfig

log = get_plugin_logger(__name__)


class NavigationManager:
    """Manages language-specific navigation structures"""

    def __init__(self, locales: List[LocaleConfig]):
        self.locales = locales
        self.language_navs: Dict[str, Navigation] = {}
        self.language_files: Dict[str, Files] = {}
        
        # Build link to lang mapping table for fast lookup (same as LanguageContextManager)
        self.link_to_lang = {}
        for locale in locales:
            # Extract the first level directory from link
            link_dir = locale.link.strip("/").split("/")[0]
            if link_dir:  # Only add non-empty directories
                self.link_to_lang[link_dir] = locale.lang

    def build_language_files(self, files: Files) -> None:
        """Build language-specific file collections (called in on_files event)"""
        
        # Pre-filter files by language for better performance
        language_file_lists = {locale.lang: [] for locale in self.locales}
        
        for file in files:
            # Use the same logic as LanguageContextManager to detect file language
            from pathlib import Path
            src_path = file.src_path
            first_dir = Path(src_path).parts[0] if Path(src_path).parts else None
            file_lang = self.link_to_lang.get(first_dir) if first_dir else None
            
            if file_lang and file_lang in language_file_lists:
                language_file_lists[file_lang].append(file)
        
        # Create Files objects for each language
        for lang, file_list in language_file_lists.items():
            self.language_files[lang] = Files(file_list)
            log.debug(f"Built file collection for language '{lang}': {len(file_list)} files")

    def build_language_navigations(self, nav: Navigation, files: Files, config: MkDocsConfig) -> None:
        """Build navigation structures for each language"""
        
        # If language files haven't been built yet, build them now
        if not self.language_files:
            self.build_language_files(files)
        
        # Create language-specific navigations using pre-built file collections
        for locale in self.locales:
            lang = locale.lang
            if lang in self.language_files:
                language_nav = self._build_navigation_for_language(config, locale)
                self.language_navs[lang] = language_nav
                log.debug(f"Built navigation for language: {lang}")

    def _build_navigation_for_language(
        self, 
        config: MkDocsConfig, 
        locale: LocaleConfig
    ) -> Navigation:
        """Build navigation for a specific language using pre-built file collection"""
        lang = locale.lang
        
        # Get pre-built file collection for this language
        language_files = self.language_files.get(lang)
        if not language_files:
            log.warning(f"No files found for language: {lang}")
            return Navigation([], [])
        
        # Create a temporary config for this language
        temp_config = config.copy()
        
        # If locale has custom nav configuration, use it
        if locale.nav:
            temp_config['nav'] = locale.nav
        else:
            # Let MkDocs auto-generate nav from filtered files
            temp_config['nav'] = None
        
        # Build navigation using MkDocs core function
        return get_navigation(language_files, temp_config)

    def _filter_files_by_language(self, files: Files, lang: str) -> Files:
        """Filter files by language and return a new Files object"""
        from pathlib import Path
        
        filtered_files = []
        
        for file in files:
            # Use the same logic as LanguageContextManager to detect file language
            src_path = file.src_path
            first_dir = Path(src_path).parts[0] if Path(src_path).parts else None
            file_lang = self.link_to_lang.get(first_dir) if first_dir else None
            
            if file_lang == lang:
                filtered_files.append(file)
        
        return Files(filtered_files)

    def get_navigation_for_language(self, lang: str) -> Optional[Navigation]:
        """Get navigation for a specific language"""
        return self.language_navs.get(lang)

    def detect_page_language(self, page: Page) -> Optional[str]:
        """Detect the language of a page (same logic as LanguageContextManager)"""
        from pathlib import Path
        
        src_path = page.file.src_path
        first_dir = Path(src_path).parts[0] if Path(src_path).parts else None
        return self.link_to_lang.get(first_dir) if first_dir else None

    def modify_navigation_context(self, context: dict, page: Page) -> dict:
        """Modify the navigation context for a page"""
        page_lang = self.detect_page_language(page)
        
        if page_lang and page_lang in self.language_navs:
            # Replace the navigation with language-specific navigation
            context["nav"] = self.language_navs[page_lang]
            log.debug(f"Set navigation for page {page.file.src_path} to language: {page_lang}")
        
        return context
