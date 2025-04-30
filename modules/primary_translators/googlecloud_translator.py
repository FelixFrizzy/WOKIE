import os
from google.cloud import translate_v3
from google.api_core.exceptions import GoogleAPICallError
from modules.primary_translators.abstract_primary_translator import PrimaryTranslationService
import argparse

class GoogleTranslationService(PrimaryTranslationService):
    """
    Translation service that uses the Google Cloud Translation API.
    """
    def __init__(self, project_id: str = None):
        # Use the provided project_id or fall back to an environment variable.
        self.project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT", "translate-ontology42") # TODO make it more flexible with google projects
        self.client = translate_v3.TranslationServiceClient()
        self.parent = f"projects/{self.project_id}/locations/global"
    
    def translate(self, term: str, source_lang: str, target_lang: str) -> str:
        # Default to "en-US" if source language is not provided. #TODO think about default language. SKOS allows also having no language tag
        src_lang = source_lang if source_lang else "en-US"
        try:
            response = self.client.translate_text(
                contents=[term],
                target_language_code=target_lang,
                parent=self.parent,
                mime_type="text/plain",  # Supported mime types: text/plain, text/html, etc.
                source_language_code=src_lang,
            )
            if response.translations:
                # Return the first translation result. #TODO can i get synonyms here too?
                #TODO I wonder if only the first word is extracted here. I thought this uses the first phrase / expression but I might be wrong, have to check this
                return response.translations[0].translated_text
            raise RuntimeError("Translation failed: No translations returned from API.")
        except (GoogleAPICallError) as e:
            msg = str(e)
            if "Source language is invalid" in msg or "Target language is invalid" in msg:
                return None
            raise RuntimeError(f"Google Translation API error: {e}") from e
        
if __name__ == "__main__":
    # Example usage of the GoogleTranslationService
    translator = GoogleTranslationService()
    term = "hello world"
    source_lang = "de"
    target_lang = "zz"
    try:
        translated_text = translator.translate(term, source_lang, target_lang)
        print(f"Translated text: {translated_text}")
    except RuntimeError as e:
        print(f"Error: {e}")


