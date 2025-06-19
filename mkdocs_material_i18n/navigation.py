"""Navigation management for MkDocs Material i18n Plugin"""

from typing import Optional
from pathlib import Path
from mkdocs.structure.nav import Navigation
from mkdocs.structure.files import Files
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import get_plugin_logger

log = get_plugin_logger(__name__)


class NavigationManager:
    """Manages language-specific navigation structures"""

    def __init__(self, locales):
        """
        Initialize the navigation manager

        Args:
            locales: List of locale configurations from plugin config
        """
        self.locales = locales
        self.locale_navs = {}

        # Build navigation configurations for each locale
        for locale in locales:
            if locale.nav is not None:
                self.locale_navs[locale.lang] = locale.nav
                log.debug(f"Configured navigation for language '{locale.lang}'")

    def has_language_navigation(self, language: str) -> bool:
        """
        Check if a specific language has custom navigation configured

        Args:
            language: Language code to check

        Returns:
            True if language has custom navigation, False otherwise
        """
        return language in self.locale_navs

    def build_navigation_for_page(self, page, config: MkDocsConfig, files: Files) -> Optional[Navigation]:
        """
        Build navigation for a specific page based on its language

        Args:
            page: Current page being processed
            config: MkDocs configuration
            files: All files in the site

        Returns:
            Language-specific navigation or None if no custom nav
        """
        # Detect page language from file path
        page_language = self._detect_page_language(page)

        if not page_language or page_language not in self.locale_navs:
            return None

        # Get navigation config for this language
        nav_config = self.locale_navs[page_language]

        # Filter files to only include files from the same language
        language_files = self._filter_files_for_language(files, page_language)

        # Build navigation using MkDocs native method
        temp_config = config
        original_nav = temp_config.nav
        temp_config.nav = nav_config

        from mkdocs.structure.nav import get_navigation
        language_nav = get_navigation(language_files, temp_config)

        # Restore original nav
        temp_config.nav = original_nav

        log.debug(f"Built navigation for language '{page_language}' with {len(language_nav.pages)} pages")
        return language_nav

    def _detect_page_language(self, page) -> Optional[str]:
        """Detect language from page file path"""
        src_path = Path(page.file.src_path)
        if not src_path.parts:
            return None

        first_dir = src_path.parts[0]

        # Check if first directory matches any configured language
        for locale in self.locales:
            lang_dir = locale.link.strip("/").split("/")[0]
            if lang_dir == first_dir:
                return locale.lang

        return None

    def _filter_files_for_language(self, files: Files, language: str) -> Files:
        """Filter files to only include files from specified language directory"""
        # Find the language directory name
        lang_dir = None
        for locale in self.locales:
            if locale.lang == language:
                lang_dir = locale.link.strip("/").split("/")[0]
                break

        if not lang_dir:
            return files

        # Filter files that belong to this language
        from mkdocs.structure.files import Files
        filtered_files = Files([])

        for file in files:
            src_path = Path(file.src_path)
            if src_path.parts and src_path.parts[0] == lang_dir:
                filtered_files.append(file)

        return filtered_files

    # ...existing code...

    def get_current_language_from_files(self, files: Files) -> Optional[str]:
        """
        Detect current build language based on files being processed

        Args:
            files: MkDocs Files collection

        Returns:
            Detected language code or None
        """
        # Check if files are under a language-specific directory
        for file in files:
            src_path = Path(file.src_path)
            if src_path.parts:
                first_dir = src_path.parts[0]
                # Check if this matches any configured locale
                for locale in self.locales:
                    link_dir = locale.link.strip("/").split("/")[0]
                    if link_dir == first_dir:
                        return locale.lang

        return None

    def get_navigation_for_language(self, language: str) -> Optional[list]:
        """
        Get the navigation configuration for a specific language

        Args:
            language: Language code

        Returns:
            Navigation configuration list or None if no custom nav
        """
        return self.locale_navs.get(language)

    def should_override_navigation(self, files: Files) -> tuple[bool, Optional[str]]:
        """
        Determine if navigation should be overridden for current build

        Args:
            files: MkDocs Files collection

        Returns:
            Tuple of (should_override, language_code)
        """
        current_language = self.get_current_language_from_files(files)

        if current_language and self.has_language_navigation(current_language):
            return True, current_language

        return False, None

    def filter_files_for_language(self, files: Files, language: str) -> Files:
        """
        Filter files collection to only include files for a specific language

        Args:
            files: MkDocs Files collection
            language: Language code to filter for

        Returns:
            Filtered Files collection containing only files for the specified language
        """
        # Find the locale configuration for this language
        locale = None
        for loc in self.locales:
            if loc.lang == language:
                locale = loc
                break

        if not locale:
            return files

        # Extract language directory from locale link
        lang_dir = locale.link.strip("/").split("/")[0]
        if not lang_dir:
            return files

        # Create a new Files collection with only files from the language directory
        from mkdocs.structure.files import Files

        filtered_files = Files([])

        for file in files:
            src_path = Path(file.src_path)
            if src_path.parts and src_path.parts[0] == lang_dir:
                filtered_files.append(file)

        return filtered_files
