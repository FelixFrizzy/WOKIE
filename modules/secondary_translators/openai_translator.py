# openai_translator.py
import logging
import os
import sys
from httpx import HTTPStatusError
from openai import OpenAI
from typing import Optional, Any
from modules.secondary_translators.abstract_secondary_translator import SecondaryTranslationService
from config import OPENAI_API_KEY

class OpenAITranslationService(SecondaryTranslationService):
    """
    Translation service that uses OpenAI (GPT).
    """
    def __init__(self, model_name: str, temperature: float = 1, logger = None):
        if not OPENAI_API_KEY:
            raise ValueError("Error: OPENAI_API_KEY is not set in the environment!")
        if not model_name:
            raise ValueError("No model selected.")
        if not 0 <= temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2 (inclusive)")
        
        self.client = OpenAI(api_key=OPENAI_API_KEY)

        self.model_name = model_name
        self.temperature = temperature
        self.service_name = "openai"
        self.logger: logging.Logger = logger or logging.getLogger(__name__)


    
    def translate_with_context(self, prompt: Any) -> Optional[str]:
        #TODO think about which models can be used
        #TODO think about default language (for now en-US). SKOS allows also having no language tag. due to refactor, must be solved somehwhere else
        if isinstance(prompt, dict):
            instructions = prompt.get("instructions", "")
            input_text = prompt.get("input", "")
        else:
            raise ValueError("Prompt must be a dictionary containing 'instructions' and 'input' keys.")

        try:
            response = self.client.responses.create(
            model=self.model_name,
            instructions=instructions,
            input=input_text,
            temperature=self.temperature, # between 0 and 2
            )
            return(response.output_text) #TODO think about error handling, what if translation fails or API not reachable etc
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