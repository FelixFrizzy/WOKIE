import requests
from modules.primary_translators.abstract_primary_translator import PrimaryTranslationService
from config import PONS_API_KEY

class PonsPaidTranslationService(PrimaryTranslationService):
    def __init__(self):
        # Store the PONS API key for use in each request
        self.base_url = "https://translate-api.pons.com/v1/translate"

    def translate(self, term: str, source_lang: str, target_lang: str) -> str:

        headers = {
            "Accept": "application/json",
            "X-PONS-APIKEY": PONS_API_KEY,
            "Content-Type": "application/json",
        }
        payload = {
            "sourceLanguage": source_lang,
            "targetLanguage": target_lang,
            "segments": [
                {"text": term}
            ]
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        # the translated text should be in segments[0].text
        try:
            return data["segments"][0]["text"]
        except (KeyError, IndexError) as e:
            raise ValueError(f"Unexpected API response structure: {data!r}") from e

    
if __name__ == "__main__":
    # Example usage of the GoogleTranslationService
    translator = PonsPaidTranslationService()
    term = "hello world"
    source_lang = "de"
    target_lang = "en"
    try:
        translated_text = translator.translate(term, source_lang, target_lang)
        print(f"Translated text: {translated_text}")
    except RuntimeError as e:
        print(f"Error: {e}")

