import translators
from translators.server import TranslatorError
from modules.primary_translators.abstract_primary_translator import PrimaryTranslationService



class TranslatecomTranslationService(PrimaryTranslationService):

    def translate(self, term: str, source_lang: str, target_lang: str) -> str | None:
        try:
            translated = translators.translate_text(term, translator="translateCom", from_language=source_lang, to_language=target_lang)
            return(translated)
        except TranslatorError as e:
            msg = str(e)
            if "Unsupported from_language" in msg or "Unsupported to_language" in msg:
                # return None if unsupported source or target language
                return None
            raise

if __name__ == "__main__":
    # Example usage of the GoogleTranslationService
    translator = TranslatecomTranslationService()
    term = "hello world"
    source_lang = "zz"
    target_lang = "yy"
    try:
        translated_text = translator.translate(term, source_lang, target_lang)
        print(f"Translated text: {translated_text}")
    except RuntimeError as e:
        print(f"Error: {e}")