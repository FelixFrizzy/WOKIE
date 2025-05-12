# deepseek_translator.py
import os
import logging
import requests
import sys
from httpx import HTTPStatusError
from google import genai
from google.genai import types
from typing import Optional, Any
from modules.secondary_translators.abstract_secondary_translator import SecondaryTranslationService
from config import GEMINI_API_KEY

class GeminiTranslationService(SecondaryTranslationService):
    """
    Translation service that uses Googles gemini model.
    """
    def __init__(self, *, model_name: str, temperature: float = 1, logger = None):
        if not GEMINI_API_KEY:
            raise ValueError("Error: GEMINI_API_KEY is not set in the environment!")
        if not model_name:
            raise ValueError("No model selected.")
        if model_name not in ("gemini-2.5-flash-preview-04-17", "gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-1.5-pro"):
            raise ValueError("Non-existing model selected.")
        if not 0 <= temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2 (inclusive)")
        
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        
        self.model_name = model_name
        self.temperature = temperature
        self.service_name = "gemini" 
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
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=input_text,
                config=types.GenerateContentConfig(
                    system_instruction=instructions,
                    temperature=self.temperature,
                ),
            )
            return(response.text) #TODO think about error handling, what if translation fails or API not reachable etc
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

