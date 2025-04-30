import translators
from translators.server import TranslatorError
from modules.primary_translators.abstract_primary_translator import PrimaryTranslationService



class LingvanexTranslationService(PrimaryTranslationService):

    def translate(self, term: str, source_lang: str, target_lang: str) -> str | None:
        lang_mapping = {
        'ar': 'ar_EG',
        'de': 'de_DE',
        'en': 'en_US',
        'es': 'es_ES',
        'fr': 'fr_FR',
        'hr': 'hr_HR',
        'hu': 'hu_HU',
        'it': 'it_IT',
        'la': 'la_VAT',
        'nl': 'nl_NL',
        'pt': 'pt_PT',
        'ru': 'ru_RU',
        'sl': 'sl_SI',
        'sr': 'sr-Cyrl_RS',
        }
        try:
            translated = translators.translate_text(term, translator="lingvanex", from_language=lang_mapping[source_lang], to_language=lang_mapping[target_lang])
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
    translator = LingvanexTranslationService()
    term = "hello world"
    source_lang = "dd"
    target_lang = "dd"
    try:
        translated_text = translator.translate(term, source_lang, target_lang)
        print(f"Translated text: {translated_text}")
    except RuntimeError as e:
        print(f"Error: {e}")
