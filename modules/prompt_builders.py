# modules/prompt_builders.py
from typing import List, Any
from modules.prompt_components import PromptComposer
from modules.prompt_formatters import OpenAIPromptFormatter, OllamaPromptFormatter, DummyPromptFormatter

class PromptBuilder:
    def __init__(self, components: List, service_name: str):
        self.composer = PromptComposer(components)
        if service_name.lower() == "openai":
            self.formatter = OpenAIPromptFormatter()
        elif service_name.lower() == "ollama":
            self.formatter = OllamaPromptFormatter()
        elif service_name.lower() == "dummy":
            self.formatter = DummyPromptFormatter()
        else:
            raise ValueError(f"Unsupported secondary translation service: {service_name}.")
            

    def build_prompt(self, target_lang: str) -> Any:
        composed_text = self.composer.compose()
        return self.formatter.format(composed_text, target_lang)
