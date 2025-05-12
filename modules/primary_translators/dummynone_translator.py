import logging
from modules.primary_translators.abstract_primary_translator import PrimaryTranslationService


class DummyNonePrimaryTranslationService(PrimaryTranslationService):
    """
    A dummy translation service for testing purposes.
    """
    def __init__(self, *, logger = None):
        # If no logger passed, use a module‐level logger
        self.logger: logging.Logger = logger or logging.getLogger(__name__)
        self.service_name = "none"
    def translate(self, term: str, source_lang: str, target_lang: str) -> str:
        # Dummy behavior: simply append the target language code.
        # return f"{term}_{target_lang}_dummy"
        return None