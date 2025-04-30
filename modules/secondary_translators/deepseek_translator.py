# deepseek_translator.py
import os
import requests
from openai import OpenAI
from typing import Optional, Any
from modules.secondary_translators.abstract_secondary_translator import SecondaryTranslationService
from config import DEEPSEEK_API_KEY

class DeepseekTranslationService(SecondaryTranslationService):
    """
    Translation service that uses Deepseek API.
    possible models: deepseek-chat (as of Apr. 2025 uses deepseek-v3), deepseek-reasoner (as of Apr. 2025 uses deepseek-r1)
    """
    def __init__(self, model_name: str, temperature: float = 1):
        if not DEEPSEEK_API_KEY:
            raise ValueError("Error: DEEPSEEK_API_KEY is not set in the environment!")
        if not model_name:
            raise ValueError("No model selected.")
        if model_name not in ("deepseek-chat", "deepseek-reasoner"):
            raise ValueError("Non-existing model selected.")
        if not 0 <= temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2 (inclusive)")
        
        self.client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
        
        self.model_name = model_name
        self.temperature = temperature
        self.service_name = "deepseek" 
    
    def translate_with_context(self, prompt: Any) -> Optional[str]:
        # Prepare prompt and instructions 
        #TODO think about default language (for now en-US). SKOS allows also having no language tag. due to refactor, must be solved somehwhere else
                
        if isinstance(prompt, dict):
            instructions = prompt.get("instructions", "")
            input_text = prompt.get("input", "")
        else:
            raise ValueError("Prompt must be a dictionary containing 'instructions' and 'input' keys.") 

                
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": f"{instructions}"},
                {"role": "user", "content": f"{input_text}"},
            ],
            stream=False
        )

        return(response.choices[0].message.content) #TODO think about error handling, what if translation fails or API not reachable etc

    # rating a translation is working the same way as translating
    rate_translation = translate_with_context