# deepseek_translator.py
import os
import logging
import requests
import sys
from httpx import HTTPStatusError
from openai import OpenAI
from typing import Optional, Any
from modules.secondary_translators.abstract_secondary_translator import SecondaryTranslationService
from config import MISTRAL_API_KEY

class MistralTranslationService(SecondaryTranslationService):
    """
    Translation service that uses Mistral API
    """
    def __init__(self, *, model_name: str, temperature: float = 1, logger = None):
        if not MISTRAL_API_KEY:
            raise ValueError("Error: MISTRAL_API_KEY is not set in the environment!")
        if not model_name:
            raise ValueError("No model selected.")
        if model_name not in ("ministral-3b-2410", "ministral-3b-latest", "ministral-8b-2410", "ministral-8b-latest", "open-mistral-7b", "mistral-tiny", "mistral-tiny-2312", "open-mistral-nemo", "open-mistral-nemo-2407", "mistral-tiny-2407", "mistral-tiny-latest", "open-mixtral-8x7b", "mistral-small", "mistral-small-2312", "open-mixtral-8x22b", "open-mixtral-8x22b-2404", "mistral-small-2402", "mistral-small-2409", "mistral-medium-2312", "mistral-medium", "mistral-medium-latest", "mistral-large-2402", "mistral-large-2407", "mistral-large-2411", "mistral-large-latest", "pixtral-large-2411", "pixtral-large-latest", "mistral-large-pixtral-2411", "codestral-2405", "codestral-2501", "codestral-latest", "codestral-2412", "codestral-2411-rc5", "codestral-mamba-2407", "open-codestral-mamba", "codestral-mamba-latest", "pixtral-12b-2409", "pixtral-12b", "pixtral-12b-latest", "mistral-small-2501", "mistral-small-2503", "mistral-small-latest", "mistral-saba-2502", "mistral-saba-latest"):
            raise ValueError("Non-existing model selected.")
        if not 0 <= temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2 (inclusive)")
        
        self.client = OpenAI(api_key=MISTRAL_API_KEY, base_url="https://api.mistral.ai/v1")
        
        self.model_name = model_name
        self.temperature = temperature
        self.service_name = "mistral" 
        self.logger: logging.Logger = logger or logging.getLogger(__name__)
    
    def translate_with_context(self, prompt: Any) -> Optional[str]:
        # Prepare prompt and instructions 
        #TODO think about default language (for now en-US). SKOS allows also having no language tag. due to refactor, must be solved somehwhere else
                
        if isinstance(prompt, dict):
            instructions = prompt.get("instructions", "")
            input_text = prompt.get("input", "")
        else:
            raise ValueError("Prompt must be a dictionary containing 'instructions' and 'input' keys.") 

        try:        
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": f"{instructions}"},
                    {"role": "user", "content": f"{input_text}"},
                ],
                stream=False
            )
            return(response.choices[0].message.content) #TODO think about error handling, what if translation fails or API not reachable etc
        except HTTPStatusError as e:
            code = e.response.status_code
            if code == 429:
                self.logger.critical(
                    f"{self.service_name} returned Too Many Requests – rate limit reached, exiting."
                )
                sys.exit(1)
            else:
                self.logger.critical(
                    f"{self.service_name} returned HTTP {code}: {e.response.text!r}"
                )
                # re-raise
                raise
        except Exception as e:
            self.logger.critical(
                f"{self.service_name} unexpected error\n Exception: {e!r} "
            )


    # rating a translation is working the same way as translating
    rate_translation = translate_with_context




