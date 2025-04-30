from deep_translator import MicrosoftTranslator
from deep_translator.exceptions import LanguageNotSupportedException
from modules.primary_translators.abstract_primary_translator import PrimaryTranslationService
from config import MICROSOFT_API_KEY



class MicrosoftTranslationService(PrimaryTranslationService):

    def translate(self, term: str, source_lang: str, target_lang: str) -> str:
        try:
            microsoft_translator = MicrosoftTranslator(
                source=source_lang,
                target=target_lang,
                api_key=MICROSOFT_API_KEY,
                region="germanywestcentral"
            )
            translated = microsoft_translator.translate(term)
            return translated
        except LanguageNotSupportedException:
            return None  # Graceful fallback for unsupported languages
        except Exception as e:
            raise # Let all other errors raise normally
    
if __name__ == "__main__":
    # Example usage of the GoogleTranslationService
    translator = MicrosoftTranslationService()
    term = "hello world"
    source_lang = "zz"
    target_lang = "yy"
    try:
        translated_text = translator.translate(term, source_lang, target_lang)
        print(f"Translated text: {translated_text}")
    except RuntimeError as e:
        print(f"Error: {e}")
