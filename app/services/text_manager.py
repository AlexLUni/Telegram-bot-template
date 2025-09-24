import json
import logging
from pathlib import Path
from typing import TypedDict

from app.constants import TEXTS_PATH


class TextData(TypedDict, total=False):
    """Type of data to extract from JSON file."""

    text: str
    parse_mode: str | None


logger = logging.getLogger(__name__)


class TextManager:
    """Handles text loading and formatting."""

    def __init__(self, file_path: str = TEXTS_PATH) -> None:
        """Set file_path and load the json file with responds."""
        self.file_path = Path(file_path)
        self.texts: dict[str, dict[str, str | TextData]] = {}
        self._load()

    def _load(self) -> None:
        """Load or reload content data."""
        try:
            with self.file_path.open(encoding='utf-8') as file:
                self.texts = json.load(file)
            logger.debug('Content data refreshed successfully')
        except json.JSONDecodeError:
            logger.exception('Invalid JSON format in content file')
            self.texts = {}
        except OSError:
            logger.exception('Failed to load JSON content file')
            self.texts = {}

    def refresh(self) -> None:
        """Public method to force reload content."""
        self._load()

    def get(self, category: str, key: str, **placeholders: str | int | None) -> tuple[str, str | None]:
        """Public method to get text with placeholders and parse mode."""
        try:
            data = self.texts[category][key]
            text = data['text'] if isinstance(data, dict) else data
            parse_mode = data.get('parse_mode') if isinstance(data, dict) else None

            if placeholders:
                return text.format(**placeholders), parse_mode
            return text, parse_mode

        except KeyError as e:
            logger.exception('Missing text: %s.%s', category, key)
            raise ValueError(f'Text not found: {category}.{key}') from e

    def get_text(self, category: str, key: str, **placeholders: str | int | None) -> str:
        """Public method to get a text without a parse mode."""
        return self.get(category, key, **placeholders)[0]


text_manager = TextManager()
