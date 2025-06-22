"""Navigation management for MkDocs Material i18n Plugin"""

from typing import Dict, List, Optional
from mkdocs.structure.nav import Navigation, get_navigation
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import get_plugin_logger

from .config import LocaleConfig
from .locale_mapper import get_locale_mapper

log = get_plugin_logger(__name__)


class NavigationManager:
    """Manages language-specific navigation structures"""

    def __init__(self, locales: List[LocaleConfig]):
        self.locales = locales
        self.language_navs: Dict[str, Navigation] = {}
        self.language_files: Dict[str, Files] = {}
        self.locale_mapper = get_locale_mapper()

    def build_language_files(self, files: Files) -> None:
        """Build language-specific file collections (called in on_files event)"""

        # Pre-filter files by language for better performance
        language_file_lists = {locale.lang: [] for locale in self.locales}
        for file in files:
            file_lang = self.locale_mapper.detect_lang_from_path(file.src_path)

            if file_lang and file_lang in language_file_lists:
                language_file_lists[file_lang].append(file)

        # Create Files objects for each language
        for lang, file_list in language_file_lists.items():
            self.language_files[lang] = Files(file_list)
            log.debug(
                f"Built file collection for language '{lang}': {len(file_list)} files"
            )

    def build_language_navigations(
        self, nav: Navigation, files: Files, config: MkDocsConfig
    ) -> None:
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
        self, config: MkDocsConfig, locale: LocaleConfig
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
            temp_config["nav"] = locale.nav
        else:
            # Let MkDocs auto-generate nav from filtered files
            temp_config["nav"] = None
        # Build navigation using MkDocs core function
        return get_navigation(language_files, temp_config)

    def detect_page_language(self, page: Page) -> Optional[str]:
        """Detect the language of a page"""
        return self.locale_mapper.detect_lang_from_path(page.file.src_path)

    def modify_navigation_context(self, context: dict, page: Page) -> dict:
        """Modify the navigation context for a page"""
        page_lang = self.detect_page_language(page)

        if page_lang and page_lang in self.language_navs:
            # Replace the navigation with language-specific navigation
            context["nav"] = self.language_navs[page_lang]
            log.debug(
                f"Set navigation for page {page.file.src_path} to language: {page_lang}"
            )

        return context
