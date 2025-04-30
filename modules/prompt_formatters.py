# modules/prompt_formatters.py
from abc import ABC, abstractmethod
from typing import Any

class PromptFormatter(ABC):
    @abstractmethod
    def format(self, composed_text: str, target_lang: str) -> Any:
        """
        Format the composed text into the structure required by the translation service.
        """
        pass


class OpenAIPromptFormatter(PromptFormatter):
    # TODO alles wird hier zweimal eingegeben, das macht eig. kein sinn
    def format(self, composed_text: str, target_lang: str) -> dict:
        instructions = (
            f"You are a machine translation system that translates a term from any language to {target_lang}.\n "
            f"To determine the correct context, use the provided additional details. Return only the translated term and nothing else."
        )
        return {"instructions": instructions, "input": composed_text}


class OllamaPromptFormatter(PromptFormatter):
    def format(self, composed_text: str, target_lang: str) -> dict:
        instructions = (
            f"You are a machine translation system that translates a term from any language to {target_lang}.\n "
        )
        input = (
            f"Here is the term to translate and additional information for better precision and to determine the correct context: \n{composed_text}\n"
            f"Return only the translated term in {target_lang} and nothing else."
        )
        return {"instructions": instructions, "input": composed_text}

class DummyPromptFormatter(PromptFormatter):
    def format(self, composed_text: str, target_lang: str) -> dict:
        instructions = (
            f"You are a machine translation system that translates a term from any language to {target_lang}.\n "
        )
        input = (
            f"Here is the term to translate and additional information for better precision and to determine the correct context: \n{composed_text}\n"
            f"Return only the translated term in {target_lang} and nothing else."
        )
        return {"instructions": instructions, "input": composed_text}
