# ollama_translator.py
import logging
from typing import Any
import sys
from httpx import HTTPStatusError
import ollama
from modules.secondary_translators.abstract_secondary_translator import SecondaryTranslationService
from modules.prompt_formatters import PromptFormatter


class OllamaTranslationService(SecondaryTranslationService):
    """
    A translation service that uses Ollama (locally running) to translate terms with context.
    Must be installed and started locally.
    Models must be pulled with `ollama pull`
    """

    def __init__(self, model_name, logger = None):

        if model_name is None:
            raise ValueError("No model selected.")
        
        self.model_name = model_name
        self.service_name = "ollama"
        self.logger: logging.Logger = logger or logging.getLogger(__name__)


    def translate_with_context(self, prompt: Any) -> str:
        if prompt is None:
            raise ValueError("Prompt is required for translation.")
        
        instructions = prompt.get("instructions", "")
        input_text = prompt.get("input", "")
        prompt_merged = instructions + input_text
        try:
            response = ollama.chat(model=self.model_name, messages=[{"role": "user", "content": prompt_merged}])
            return response["message"]["content"].strip()
        except Exception as e:
            self.logger.critical(
                f"{self.service_name} unexpected error\n Exception: {e!r} "
            )

    

    # rating a translation is working the same way as translating
    rate_translation = translate_with_context

