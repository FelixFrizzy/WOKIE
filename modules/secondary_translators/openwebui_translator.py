# openwebui_translator.py
import logging
import os
import sys
from httpx import HTTPStatusError
from openai import OpenAI
from typing import Optional, Any
from modules.secondary_translators.abstract_secondary_translator import SecondaryTranslationService
from config import OPENWEBUI_BASE_URL, OPENWEBUI_API_KEY

class OpenWebUITranslationService(SecondaryTranslationService):
    """
    Translation service that uses an openwebui-instance.
    """
    def __init__(self, model_name: str, temperature: float = 1, logger = None):
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
        self.service_name = "openwebui"
        self.logger: logging.Logger = logger or logging.getLogger(__name__)

    def extract_last_line(self,response_content):
        """
        Given any multi-line string `raw`, return the very last non-empty line,
        stripped of surrounding whitespace and quotes.
        """
        # Split into lines
        lines = response_content.splitlines()
        # Iterate from the end to find the first non-blank line
        for line in reversed(lines):
            # Remove leading/trailing whitespace and any wrapping quotes
            cleaned = line.strip().strip('"').strip("'")
            if cleaned:
                return cleaned
        # If all lines are blank, return empty string
        return ""
    
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

            return(self.extract_last_line(response.choices[0].message.content)) #TODO think about error handling, what if translation fails or API not reachable etc
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
    

