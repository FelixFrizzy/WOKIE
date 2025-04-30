# ollama_translator.py
from typing import Any
import ollama
from modules.secondary_translators.abstract_secondary_translator import SecondaryTranslationService
from modules.prompt_formatters import PromptFormatter


class OllamaTranslationService(SecondaryTranslationService):
    """
    A translation service that uses Ollama to translate terms with context.
    possible Models: llama3.2, deepseek-r1:1.5b
    #TODO add more possible models
    """

    def __init__(self, model_name):
        """
        Initializes the translation service with a model and context.
        
        model_name: The name of the Ollama model to use.
        context: The context to provide for translations (must not be None).
        """
        if model_name is None:
            raise ValueError("No model selected.")
        
        self.model_name = model_name
        self.service_name = "ollama"

    def translate_with_context(self, prompt: Any) -> str:
        """
        TODO docstring missing
        """
        if prompt is None:
            raise ValueError("Prompt is required for translation.")
        
        instructions = prompt.get("instructions", "")
        input_text = prompt.get("input", "")
        prompt_merged = instructions + input_text
        response = ollama.chat(model=self.model_name, messages=[{"role": "user", "content": prompt_merged}])
        return response["message"]["content"].strip()

    # rating a translation is working the same way as translating
    rate_translation = translate_with_context

