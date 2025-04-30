# openai_translator.py
import os
from openai import OpenAI
from typing import Optional, Any
from modules.secondary_translators.abstract_secondary_translator import SecondaryTranslationService
from config import OPENWEBUI_BASE_URL, OPENWEBUI_API_KEY

class OpenWebUITranslationService(SecondaryTranslationService):
    """
    Translation service that uses OpenAI (GPT).
    possible models: depends on instance
    #TODO add more possible models including info about costs
    """
    def __init__(self, model_name: str, temperature: float = 1):
        if not OPENWEBUI_BASE_URL:
            raise ValueError("Error: OPENWEBUI_BASE_URL is not set in the environment!")
        if not OPENWEBUI_API_KEY:
            raise ValueError("Error: OPENWEBUI_API_KEY is not set in the environment!")
        if not model_name:
            raise ValueError("No model selected.")
        if not 0 <= temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2 (inclusive)")
        
        self.client = OpenAI(api_key=OPENWEBUI_API_KEY, base_url=OPENWEBUI_BASE_URL)

        self.model_name = model_name
        self.temperature = temperature
        self.service_name = "openai"
    
    def translate_with_context(self, prompt: Any) -> Optional[str]:
        #TODO think about which models can be used
        #TODO think about default language (for now en-US). SKOS allows also having no language tag. due to refactor, must be solved somehwhere else
        if isinstance(prompt, dict):
            instructions = prompt.get("instructions", "")
            input_text = prompt.get("input", "")
        else:
            raise ValueError("Prompt must be a dictionary containing 'instructions' and 'input' keys.")
    
        response = self.client.chat.completions.create(
            model=self.model_name,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": instructions},
                {
                    "role": "user",
                    "content": input_text,
                },
            ],
        )

        return(response.choices[0].message.content) #TODO think about error handling, what if translation fails or API not reachable etc
    
    # rating a translation is working the same way as translating
    rate_translation = translate_with_context
    

if __name__ == "__main__":
    models = ["to-be-filled"]
    for model in models:
        print(model)
        try:
            service = OpenWebUITranslationService(model_name=model)  # Adjust model name if needed
            # Simulate a prompt dictionary.
            prompt = {
                "instructions": (
                    f"You are friendly"
                ),
                "input": f"Say Hello"
            }
            translation = service.translate_with_context(prompt)
            print(translation)
        except Exception as e:
            print(f"An error occurred: {e}")
