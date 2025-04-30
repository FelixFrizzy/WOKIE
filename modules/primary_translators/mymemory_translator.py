import translators
from translators.server import TranslatorError
from modules.primary_translators.abstract_primary_translator import PrimaryTranslationService



class MyMemoryTranslationService(PrimaryTranslationService):

    def translate(self, term: str, source_lang: str, target_lang: str) -> str | None:
        lang_mapping = {
        'ar': 'ar-EG',
        'de': 'de-DE',
        'en': 'en-US',
        'es': 'es-ES',
        'fr': 'fr-FR',
        'hr': 'hr-HR',
        'hu': 'hu-HU',
        'it': 'it-IT',
        'la': 'la-VA',
        'nl': 'nl-NL',
        'pt': 'pt-PT',
        'ru': 'ru-RU',
        'sl': 'sl-SI',
        'sr': 'sr-Cyrl-RS',
        }
        try:
            translated = translators.translate_text(term, translator="myMemory", from_language=lang_mapping[source_lang], to_language=lang_mapping[target_lang])
            return(translated)
        except KeyError as e:
            return None
        except TranslatorError as e:
            msg = str(e)
            if "Unsupported from_language" in msg or "Unsupported to_language" in msg:
                # return None if unsupported source or target language
                return None
            raise

if __name__ == "__main__":
    # Example usage of the GoogleTranslationService
    translator = MyMemoryTranslationService()
    term = "hello world"
    source_lang = "zz"
    target_lang = "yy"
    try:
        translated_text = translator.translate(term, source_lang, target_lang)
        print(f"Translated text: {translated_text}")
    except RuntimeError as e:
        print(f"Error: {e}")