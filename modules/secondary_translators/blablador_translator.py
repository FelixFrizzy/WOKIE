# openai_translator.py
import logging
import os
import re
import sys
from httpx import HTTPStatusError
from openai import OpenAI
from typing import Optional, Any
from modules.secondary_translators.abstract_secondary_translator import SecondaryTranslationService
from config import BLABLADOR_BASE_URL, BLABLADOR_API_KEY

class BlabladorTranslationService(SecondaryTranslationService):
    """
    Translation service that uses Blablador.
    """
    def __init__(self, model_name: str, temperature: float = 1, logger = None):
        if not BLABLADOR_BASE_URL:
            raise ValueError("Error: OPENWEBUI_BASE_URL is not set in the environment!")
        if not BLABLADOR_API_KEY:
            raise ValueError("Error: OPENWEBUI_API_KEY is not set in the environment!")
        if not model_name:
            raise ValueError("No model selected.")
        if not 0 <= temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2 (inclusive)")
        
        self.client = OpenAI(api_key=BLABLADOR_API_KEY, base_url=BLABLADOR_BASE_URL)

        self.model_name = model_name
        self.temperature = temperature
        self.service_name = "blablador"
        self.logger: logging.Logger = logger or logging.getLogger(__name__)

    def remove_think_content(self,response_content):
    # remove <think> tags and all content insidethat might be in the response
        cleaned = re.sub(r"(?is)<think>.*?</think>\s*", "", response_content)
        return cleaned


    def translate_with_context(self, prompt: Any) -> Optional[str]:
        #TODO think about which models can be used
        #TODO think about default language (for now en-US). SKOS allows also having no language tag. due to refactor, must be solved somehwhere else
        if isinstance(prompt, dict):
            instructions = prompt.get("instructions", "")
            input_text = prompt.get("input", "")
        else:
            raise ValueError("Prompt must be a dictionary containing 'instructions' and 'input' keys.")
    
        try:
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

            return(self.remove_think_content(response.choices[0].message.content)) #TODO think about error handling, what if translation fails or API not reachable etc
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
    
