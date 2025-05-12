from modules.secondary_translators.abstract_secondary_translator import SecondaryTranslationService

class DummySecondaryTranslationService(SecondaryTranslationService):
    def __init__(self):
        self.service_name = "dummy"
        self.model_name = "dummy_model"

    def translate_with_context(self, prompt: dict) -> str:
        label = None

        if isinstance(prompt, dict):
            # Handle dict-based prompt
            label = prompt.get("input", "").strip()
            for line in label.splitlines():
                if line.startswith("Term to translate:"):
                    label = line.split(":", 1)[1].strip()
                    break
        else:
            raise ValueError(f"Prompt must be a dictionary containing 'instructions' and 'input' keys, but is of type {type(prompt)} with content {prompt}.")

        if not label:
            raise ValueError("Could not extract term label from prompt.")

        # Dummy output: simulate translation
        return f"{label}_dummy"
    
    rate_translation = translate_with_context