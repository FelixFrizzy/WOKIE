# anthropic_translator.py
import logging
import os
import anthropic
import json
import sys
from httpx import HTTPStatusError
from typing import Optional, Any
from modules.secondary_translators.abstract_secondary_translator import SecondaryTranslationService
from config import ANTHROPIC_API_KEY


class AnthropicTranslationService(SecondaryTranslationService):
    """
    Translation service that uses Anthropic SDK (claude).
    possible models: 'claude-3-7-sonnet-20250219', 'claude-3-5-sonnet-20241022', 'claude-3-5-haiku-20241022', 'claude-3-5-sonnet-20240620', 'claude-3-haiku-20240307', 'claude-3-opus-20240229'
    """
    def __init__(self, model_name: str, temperature: float = 1, logger = None):
        if not ANTHROPIC_API_KEY:
            raise ValueError("Error: ANTHROPIC_API_KEY is not set in the environment!")
        if not model_name:
            raise ValueError("No model selected.")
        if not 0 <= temperature <= 1:
            raise ValueError("Temperature must be between 0 and 1 (inclusive)")
        
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.max_tokens = 1024
        self.model_name = model_name
        self.temperature = temperature
        self.service_name = "anthropic"
        self.logger: logging.Logger = logger or logging.getLogger(__name__)

    def get_models(self):
        models = self.client.models.list()
        return(models)
    
    def translate_with_context(self, prompt: Any) -> Optional[str]:
        if isinstance(prompt, dict):
            instructions = prompt.get("instructions", "")
            input_text = prompt.get("input", "")
        else:
            raise ValueError("Prompt must be a dictionary containing 'instructions' and 'input' keys.")
    
        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system = instructions,
                messages=[
                    {"role": "user", "content": input_text,
                    },
                ],
            )
            # Response is made up of TextBlocks
            # first convert it to json, then to python dict
            response_data = json.loads(response.to_json())

            # iterate over resp_data["content"] and join all the text blocks (usually only one text block)
            text_only = "".join(
                block["text"]
                for block in response_data["content"]
                if block.get("type") == "text"
            )

            return(text_only) #TODO think about error handling, what if translation fails or API not reachable etc
        
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
    
