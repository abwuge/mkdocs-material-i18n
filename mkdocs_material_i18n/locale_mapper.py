"""Locale mapping singleton for MkDocs Material i18n Plugin"""

from typing import Dict, List, Optional
from pathlib import Path
from mkdocs.plugins import get_plugin_logger

from .config import LocaleConfig

log = get_plugin_logger(__name__)


class LocaleMapper:
    """
    Singleton class for managing locale mappings from link directories to locale configurations.

    This class provides a centralized way to map link directories (first level directories in paths)
    to their corresponding locale configurations, eliminating the need for duplicate link_to_lang
    mappings across multiple classes.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LocaleMapper, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Prevent re-initialization
        if LocaleMapper._initialized:
            return

        self.link2locale: Dict[str, LocaleConfig] = {}
        self._locales: List[LocaleConfig] = []
        LocaleMapper._initialized = True
        log.debug("LocaleMapper singleton initialized")

    def initialize(self, locales: List[LocaleConfig]) -> None:
        """
        Initialize the mapper with locale configurations.

        Args:
            locales: List of locale configurations
        """
        self._locales = locales
        self.link2locale.clear()

        for locale in locales:
            # Extract the first level directory from link
            link_dir = locale.link.strip("/").split("/")[0]
            if link_dir:  # Only add non-empty directories
                self.link2locale[link_dir] = locale
                log.debug(
                    f"Mapped link directory '{link_dir}' to locale '{locale.lang}'"
                )

        log.info(
            f"LocaleMapper initialized with {len(self.link2locale)} locale mappings"
        )

    def get_locale_by_link_dir(self, link_dir: str) -> Optional[LocaleConfig]:
        """
        Get locale configuration by link directory.

        Args:
            link_dir: First level directory from a link path

        Returns:
            LocaleConfig instance or None if not found
        """
        return self.link2locale.get(link_dir)

    def get_lang_by_link_dir(self, link_dir: str) -> Optional[str]:
        """
        Get language code by link directory.

        Args:
            link_dir: First level directory from a link path

        Returns:
            Language code string or None if not found
        """
        locale = self.link2locale.get(link_dir)
        return locale.lang if locale else None

    def detect_locale_from_path(self, src_path: str) -> Optional[LocaleConfig]:
        """
        Detect locale from a source file path.

        Args:
            src_path: Source file path

        Returns:
            LocaleConfig instance or None if not detected
        """
        first_dir = Path(src_path).parts[0] if Path(src_path).parts else None
        return self.get_locale_by_link_dir(first_dir) if first_dir else None

    def detect_lang_from_path(self, src_path: str) -> Optional[str]:
        """
        Detect language code from a source file path.

        Args:
            src_path: Source file path

        Returns:
            Language code string or None if not detected
        """
        locale = self.detect_locale_from_path(src_path)
        return locale.lang if locale else None

    def get_all_locales(self) -> List[LocaleConfig]:
        """
        Get all locale configurations.

        Returns:
            List of all LocaleConfig instances
        """
        return self._locales.copy()

    def get_all_link_dirs(self) -> List[str]:
        """
        Get all link directories.

        Returns:
            List of all link directory strings
        """
        return list(self.link2locale.keys())

    def is_initialized(self) -> bool:
        """
        Check if the mapper has been initialized with locales.

        Returns:
            True if initialized, False otherwise
        """
        return bool(self.link2locale)

    def reset(self) -> None:
        """
        Reset the mapper (mainly for testing purposes).
        """
        self.link2locale.clear()
        self._locales.clear()
        log.debug("LocaleMapper reset")

    def get_locale_by_page(self, page) -> Optional[LocaleConfig]:
        """
        Get locale configuration by MkDocs page.

        Args:
            page: MkDocs Page instance

        Returns:
            LocaleConfig instance or None if not found
        """
        return self.detect_locale_from_path(page.file.src_path)

    def get_lang_by_page(self, page) -> Optional[str]:
        """
        Get language code by MkDocs page.

        Args:
            page: MkDocs Page instance

        Returns:
            Language code string or None if not found
        """
        locale = self.get_locale_by_page(page)
        return locale.lang if locale else None

    def has_locale_for_path(self, src_path: str) -> bool:
        """
        Check if there's a locale mapping for the given path.

        Args:
            src_path: Source file path

        Returns:
            True if a locale is found, False otherwise"""
        return self.detect_locale_from_path(src_path) is not None


# Convenience function to get the singleton instance
def get_locale_mapper() -> LocaleMapper:
    """
    Get the LocaleMapper singleton instance.

    Returns:
        LocaleMapper singleton instance
    """
    return LocaleMapper()
