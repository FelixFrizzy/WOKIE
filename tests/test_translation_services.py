import pytest
from modules.primary_translators.argos_translator import ArgosTranslationService
from modules.primary_translators.googlecloud_translator import GoogleTranslationService
from modules.primary_translators.lingvanex_translator import LingvanexTranslationService
from modules.primary_translators.modernmt_translator import ModernMTTranslationService
from modules.primary_translators.microsoft_translator import MicrosoftTranslationService
from modules.primary_translators.mymemory_translator import MyMemoryTranslationService
from modules.primary_translators.pons_translator import PonsTranslationService
from modules.primary_translators.pons_paid_translator import PonsPaidTranslationService
from modules.primary_translators.reverso_translator import ReversoTranslationService
from modules.primary_translators.translatecom_translator import TranslatecomTranslationService
from modules.primary_translators.yandex_translator import YandexTranslationService
from modules.secondary_translators.ollama_translator import OllamaTranslationService
from modules.secondary_translators.openai_translator import OpenAITranslationService
from modules.secondary_translators.openwebui_translator import OpenWebUITranslationService
from modules.secondary_translators.deepseek_translator import DeepseekTranslationService

# Test data for primary and secondary services
test_data_primary = [
    # ("May", "en", "fr"),
    # ("the", "en", "es"),
    ("force", "en", "de"),
    # ("be", "en", "it"),
    # ("with", "en", "nl"),
]

test_data_secondary = [
    ("May", "en", "fr", "written text"),
    # ("the", "en", "es", "written text"),
    # ("force", "en", "de", "written text"),
    # ("be", "en", "it", "written text"),
    # ("with", "en", "nl", "written text"),
]

# -------------------------------
# Primary translation services
# -------------------------------

@pytest.mark.parametrize("term, src_lang, target_lang", test_data_primary)
def test_argos_translator(term, src_lang, target_lang):
    service = ArgosTranslationService()
    translation = service.translate(term, src_lang, target_lang)
    assert translation and isinstance(translation, str), f"Translation of '{term}' from {src_lang} to {target_lang} should not be empty"

@pytest.mark.parametrize("term, src_lang, target_lang", test_data_primary)
def test_google_translator(term, src_lang, target_lang):
    service = GoogleTranslationService()
    translation = service.translate(term, src_lang, target_lang)
    assert translation and isinstance(translation, str), f"Translation of '{term}' from {src_lang} to {target_lang} should not be empty"

@pytest.mark.parametrize("term, src_lang, target_lang", test_data_primary)
def test_lingvanex_translator(term, src_lang, target_lang):
    service = LingvanexTranslationService()
    translation = service.translate(term, src_lang, target_lang)
    assert translation and isinstance(translation, str), f"Translation of '{term}' from {src_lang} to {target_lang} should not be empty"

@pytest.mark.parametrize("term, src_lang, target_lang", test_data_primary)
def test_modernmt_translator(term, src_lang, target_lang):
    service = ModernMTTranslationService()
    translation = service.translate(term, src_lang, target_lang)
    assert translation and isinstance(translation, str), f"Translation of '{term}' from {src_lang} to {target_lang} should not be empty"

@pytest.mark.parametrize("term, src_lang, target_lang", test_data_primary)
def test_microsoft_translator(term, src_lang, target_lang):
    service = MicrosoftTranslationService()
    translation = service.translate(term, src_lang, target_lang)
    assert translation and isinstance(translation, str), f"Translation of '{term}' from {src_lang} to {target_lang} should not be empty"

@pytest.mark.parametrize("term, src_lang, target_lang", test_data_primary)
def test_mymemory_translator(term, src_lang, target_lang):
    service = MyMemoryTranslationService()
    translation = service.translate(term, src_lang, target_lang)
    assert translation and isinstance(translation, str), f"Translation of '{term}' from {src_lang} to {target_lang} should not be empty"

@pytest.mark.parametrize("term, src_lang, target_lang", test_data_primary)
def test_pons_translator(term, src_lang, target_lang):
    service = PonsTranslationService()
    translation = service.translate(term, src_lang, target_lang)
    assert translation and isinstance(translation, str), f"Translation of '{term}' from {src_lang} to {target_lang} should not be empty"

@pytest.mark.parametrize("term, src_lang, target_lang", test_data_primary)
def test_pons_paid_translator(term, src_lang, target_lang):
    service = PonsPaidTranslationService()
    translation = service.translate(term, src_lang, target_lang)
    assert translation and isinstance(translation, str), f"Translation of '{term}' from {src_lang} to {target_lang} should not be empty"


@pytest.mark.parametrize("term, src_lang, target_lang", test_data_primary)
def test_reverso_translator(term, src_lang, target_lang):
    service = ReversoTranslationService()
    translation = service.translate(term, src_lang, target_lang)
    assert translation and isinstance(translation, str), f"Translation of '{term}' from {src_lang} to {target_lang} should not be empty"

@pytest.mark.parametrize("term, src_lang, target_lang", test_data_primary)
def test_translatecom_translator(term, src_lang, target_lang):
    service = TranslatecomTranslationService()
    translation = service.translate(term, src_lang, target_lang)
    assert translation and isinstance(translation, str), f"Translation of '{term}' from {src_lang} to {target_lang} should not be empty"

@pytest.mark.parametrize("term, src_lang, target_lang", test_data_primary)
def test_yandex_translator(term, src_lang, target_lang):
    service = YandexTranslationService()
    translation = service.translate(term, src_lang, target_lang)
    assert translation and isinstance(translation, str), f"Translation of '{term}' from {src_lang} to {target_lang} should not be empty"


# -------------------------------
# Secondary translation services
# -------------------------------

def build_prompt_dict(term, target_lang, context):
    prompt = {}
    prompt["instructions"] = f"You are a professional translator. Translate to {target_lang} using the following context:\n{context}\n Return only the translated term."
    prompt["input"] = f"Term to translate: {term}"
    return prompt

def build_prompt_str(term, target_lang, context):
    prompt = (
        f"Translate to {target_lang}.\n"
        f"Context:\n{context}\n"
        f"Term to translate: {term}"
    )
    return prompt


# Test for Ollama translation service
# We'll simulate a prompt string that matches the expected format.
@pytest.mark.parametrize("term, src_lang, target_lang, context", test_data_secondary)
def test_ollama_translator(term, src_lang, target_lang, context):
    service = OllamaTranslationService(model_name="llama3.2")  # Adjust model name if needed
    # Simulate a prompt string. For Ollama, our format is a plain string.
    # Ensure it contains "Term to translate:" so the dummy service can extract it.
    prompt = build_prompt_str(term, target_lang, context)
    translation = service.translate_with_context(prompt)
    print(translation)
    # Check that the translation is non-empty and a string.
    assert translation and isinstance(translation, str), f"Translation of '{term}' from {src_lang} to {target_lang} should not be empty"

# Test for OpenAI translation service
# We'll simulate a prompt as a dictionary (instructions and input).
@pytest.mark.parametrize("term, src_lang, target_lang, context", test_data_secondary)
def test_openai_translator(term, src_lang, target_lang, context):
    service = OpenAITranslationService(model_name="gpt-3.5-turbo")  # Adjust model name if needed
    # Simulate a prompt dictionary.
    prompt = build_prompt_dict(term, target_lang, context)
    translation = service.translate_with_context(prompt)
    print(translation)
    # Check that the translation is non-empty and is a string.
    assert translation and isinstance(translation, str), f"Translation of '{term}' from {src_lang} to {target_lang} should not be empty"

# Test for OpenWebUI translation service
# We'll simulate a prompt as a dictionary (instructions and input).
@pytest.mark.parametrize("term, src_lang, target_lang, context", test_data_secondary)
def test_openwebui_translator(term, src_lang, target_lang, context):
    service = OpenWebUITranslationService(model_name="gpt-4o-mini")  # Adjust model name if needed
    # Simulate a prompt dictionary.
    prompt = build_prompt_dict(term, target_lang, context)

    translation = service.translate_with_context(prompt)
    print(translation)
    # Check that the translation is non-empty and is a string.
    assert translation and isinstance(translation, str), f"Translation of '{term}' from {src_lang} to {target_lang} should not be empty"


# Test for Deepseek translation service
# We'll simulate a prompt as a dictionary (instructions and input).
@pytest.mark.parametrize("term, src_lang, target_lang, context", test_data_secondary)
def test_deepseek_translator(term, src_lang, target_lang, context):
    service = DeepseekTranslationService(model_name="deepseek-chat")  # Adjust model name if needed
    # Simulate a prompt dictionary.
    prompt = build_prompt_dict(term, target_lang, context)

    translation = service.translate_with_context(prompt)
    print(translation)
    # Check that the translation is non-empty and is a string.
    assert translation and isinstance(translation, str), f"Translation of '{term}' from {src_lang} to {target_lang} should not be empty"

