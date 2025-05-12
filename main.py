# main.py
import argparse
import os
import logging
from datetime import datetime
from modules.translation_pipeline import TranslationPipeline
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
from modules.primary_translators.dummynone_translator import DummyNonePrimaryTranslationService
from modules.secondary_translators.ollama_translator import OllamaTranslationService
from modules.secondary_translators.openai_translator import OpenAITranslationService
from modules.secondary_translators.anthropic_translator import AnthropicTranslationService
from modules.secondary_translators.blablador_translator import BlabladorTranslationService
from modules.secondary_translators.openwebui_translator import OpenWebUITranslationService
from modules.secondary_translators.mistral_translator import MistralTranslationService
from modules.secondary_translators.deepseek_translator import DeepseekTranslationService
from modules.secondary_translators.gemini_translator import GeminiTranslationService
from modules.secondary_translators.dummy_secondary_translator import DummySecondaryTranslationService
from modules.frequency_confidence_calculator import FrequencyConfidenceCalculator
from modules.llm_confidence_calculator import LLMConfidenceCalculator
from modules.dummy_secondary_confidence_calculator import DummySecondaryConfidenceCalculator
from config import DEBUG


def main():
    # All argparse arguments
    parser = argparse.ArgumentParser(description="Translate a SKOS file to the desired language")
    parser.add_argument("-i", "--input", required=True, 
                        help="Path to the source SKOS file")
    parser.add_argument("--language", required=True, 
                        help="Target language as IETF BCP 47 tag (e.g. de)")
    parser.add_argument("--context", default="", 
                        help="Topic or Context of source vocabulary")
    parser.add_argument("--threshold", type=float, default=0.66, 
                        help="Threshold for decision if secondary translation services are used to refine translations")
    parser.add_argument("--primary_translation", required=True, nargs='+', choices=["argos", "google", "lingvanex", "microsoft", "modernmt", "ponspaid", "reverso", "yandex", "dummynone"], 
                        help="Primary (deterministic) translation service. Options: argos, google, lingvanex, microsoft, modernmt, ponspaid, reverso, yandex")
    parser.add_argument("--secondary_translation", required=True, choices=["claude-3-5-haiku", "claude-3-5-sonnet", "claude-3-7-sonnet", "claude-3-haiku", "codestral-latest", "codestral-mamba-latest", "deepseek-chat", "deepseek-reasoner", "gemini-1.5-flash-8b", "gemini-1.5-flash", "gemini-2.0-flash-lite", "gemini-2.0-flash", "gemini-2.5-flash-preview-04-17", "gemma3:12b(openwebui)", "gpt-3.5-turbo", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-4.1(openwebui)", "gpt-4o-mini", "gpt-4o", "llama-4-maverick:free(openwebui)", "ministral-3b-latest", "ministral-8b-latest", "mistral-large-latest", "mistral-medium-latest", "mistral-small-latest", "mistral-tiny-latest", "open-mistral-nemo", "open-mixtral-8x22b", "dummy"],
                        help="Secondary (language-model based) translation service. Options: claude-3-5-haiku, claude-3-5-sonnet, claude-3-7-sonnet, claude-3-haiku, claude-3-opus, codestral-latest, codestral-mamba-latest, deepseek-chat, deepseek-reasoner, gemini-1.5-flash-8b, gemini-1.5-flash, gemini-2.0-flash-lite, gemini-2.0-flash, gemini-2.5-flash-preview-04-17, gemma3:12b(openwebui), gpt-3.5-turbo, gpt-4.1-mini, gpt-4.1-nano, gpt-4.1(openwebui), gpt-4o-mini, gpt-4o, llama-4-maverick:free(openwebui), ministral-3b-latest, ministral-8b-latest, mistral-large-latest, mistral-medium-latest, mistral-small-latest, mistral-tiny-latest, open-mistral-nemo, open-mixtral-8x22b, dummy")
    parser.add_argument("--secondary_strategy", required=False, default="individual", choices=["individual", "batch", "hierarchy"],
                        help="Secondary translation strategy. Options: individual, batch, hierarchy")
    parser.add_argument("--min_primary_translations", type=int, required=False, default="5", choices=range(1,9),
                        help="Required number of translations of a single term before the primary confidence calculator is called. Between 1 and 8 with 8 being the number maximum number of primary services.")
    parser.add_argument("--max_retries", type=int, required=False, default="1", choices=range(0,11),
                        help="Maximum number of retry attempts (0–10) if the LLM response doesn't match the required format. Capped at 10 to prevent infinite retries.")
    parser.add_argument("--temperature", type=float, required=False, default="0",
                        help="Controls randomness in generation (0.0 = deterministic, higher = more random). Must be between 0.0 and 2.0. Effect of temperature settings varies across models and providers")
    parser.add_argument("--enable-logging", action="store_true", 
                        help="Enable logging")
    args = parser.parse_args()

    # Needed for logs and filenames
    start_time = datetime.now()
    start_time_str = start_time.strftime("%Y-%m-%d_%H-%M-%S")



    logger = None
    if args.enable_logging:
        # Setup logging: the log file will be in the same folder as this main script.
        dirname, basename = os.path.split(args.input)
        basename = basename.split(".")[0]
        # Store log file in folder of input file
        log_file = os.path.join(dirname, f"log_{basename}__{args.language}_{args.threshold}_{args.primary_translation}_{args.secondary_translation}_{args.secondary_strategy}_{args.temperature}_{start_time_str}.log")


        logging.basicConfig(
            filename=log_file,
            filemode="w",
            # select DEBUG to also see the prompts in logs
            # level=logging.INFO,
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger()

        # Remove HTTP request INFO from logfile to improve log readablility
        class NoHttpRequestFilter(logging.Filter):
            def filter(self, record):
                # Drop log message about HTTP Requests
                return "HTTP Request:" not in record.getMessage()
        # Apply filter
        for handler in logger.handlers:
            handler.addFilter(NoHttpRequestFilter())


    if logger:
        logger.info(f"Script started at {start_time_str}")
        logger.info(f"Input file: {args.input}")
        logger.info(f"Target language: {args.language}")
        logger.info(f"Primary translation service: {args.primary_translation}")
        logger.info(f"Secondary translation services: {args.secondary_translation}")
        logger.info(f"Secondary translation strategy: {args.secondary_strategy}")
        logger.info(f"User provided context: {args.context}")
        logger.info(f"Max. retries for secondary confidence calculator: {args.max_retries}")
        logger.info(f"Temperature for secondary confidence calculator: {args.temperature}")
        logger.info(f"Minimal number of primary translations before calling primary confidence calculator: {args.min_primary_translations}")
        logger.info(f"Threshold: {args.threshold}")

    # Dictionary for mapping secondary service names to their respective classes
    primary_translation_services_mapping = {
        "argos": ArgosTranslationService, 
        "google": GoogleTranslationService,
        "lingvanex": LingvanexTranslationService, 
        "microsoft": MicrosoftTranslationService,  
        "modernmt": ModernMTTranslationService,  
        "ponspaid": PonsPaidTranslationService,  
        "reverso": ReversoTranslationService,  
        "yandex": YandexTranslationService,
        "dummynone": DummyNonePrimaryTranslationService
    }

    primary_translation_services = []
    for service_name in args.primary_translation:
        try:
            service_class = primary_translation_services_mapping[service_name]
        except KeyError:
            raise ValueError(f"Primary translation service {service_name} is currently not implemented")
        
        service_instance = service_class(logger=logger)
        primary_translation_services.append(service_instance)
        if logger:
            logger.info(f"Primary translation service {service_name} instantiated successfully")

    if logger:
        chosen_services = ", ".join(args.primary_translation)
        logger.info(f"Order of primary translation services (first in list used first in translations): {chosen_services}")


    # Dictionary for mapping secondary service names to their respective classes
    # Use lambda to delay execution because certain Translation services requires args.model which is not present at dict initialization. Also avoid unneccesary object creation
    secondary_translation_services_mapping = {
        "dummy": lambda: DummySecondaryTranslationService(),
        "claude-3-5-haiku": lambda: AnthropicTranslationService(model_name="claude-3-5-haiku-20241022", temperature=args.temperature),
        "claude-3-5-sonnet": lambda: AnthropicTranslationService(model_name="claude-3-5-sonnet-20241022", temperature=args.temperature),
        "claude-3-7-sonnet": lambda: AnthropicTranslationService(model_name="claude-3-7-sonnet-20250219", temperature=args.temperature),
        "claude-3-haiku": lambda: AnthropicTranslationService(model_name="claude-3-haiku-20240307", temperature=args.temperature),
        # "claude-3-opus": lambda: AnthropicTranslationService(model_name="claude-3-opus-20240229", temperature=args.temperature),
        "codestral-latest": lambda: MistralTranslationService(model_name = "codestral-latest", temperature=args.temperature),
        "codestral-mamba-latest": lambda: MistralTranslationService(model_name = "codestral-mamba-latest", temperature=args.temperature),
        "deepseek-chat": lambda: DeepseekTranslationService(model_name="deepseek-chat"), 
        "deepseek-reasoner": lambda: DeepseekTranslationService(model_name="deepseek-reasoner"), 
        "gemini-1.5-flash-8b": lambda: GeminiTranslationService(model_name = "gemini-1.5-flash-8b", temperature=args.temperature),
        "gemini-1.5-flash": lambda: GeminiTranslationService(model_name = "gemini-1.5-flash", temperature=args.temperature),
        "gemini-2.0-flash-lite": lambda: GeminiTranslationService(model_name = "gemini-2.0-flash-lite", temperature=args.temperature),
        "gemini-2.0-flash": lambda: GeminiTranslationService(model_name = "gemini-2.0-flash", temperature=args.temperature),
        "gemini-2.5-flash-preview-04-17": lambda: GeminiTranslationService(model_name = "gemini-2.5-flash-preview-04-17", temperature=args.temperature),
        "gemma3:12b(openwebui)": lambda: OpenWebUITranslationService(model_name = "gemma3:12b", temperature=args.temperature),
        "gpt-3.5-turbo": lambda: OpenAITranslationService(model_name="gpt-3.5-turbo", temperature=args.temperature),
        "gpt-4.1-mini": lambda: OpenAITranslationService(model_name = "gpt-4.1-mini", temperature=args.temperature),
        "gpt-4.1-nano": lambda: OpenAITranslationService(model_name = "gpt-4.1-nano", temperature=args.temperature),
        "gpt-4.1(openwebui)": lambda: OpenWebUITranslationService(model_name = "gpt-4.1", temperature=args.temperature),
        "gpt-4o-mini": lambda: OpenAITranslationService(model_name="gpt-4o-mini", temperature=args.temperature),
        "gpt-4o": lambda: OpenAITranslationService(model_name="gpt-4o", temperature=args.temperature),
        "llama-4-maverick:free(openwebui)": lambda: OpenWebUITranslationService(model_name = "meta-llama/llama-4-maverick:free", temperature=args.temperature),
        "ministral-3b-latest": lambda: MistralTranslationService(model_name = "ministral-3b-latest", temperature=args.temperature),
        "ministral-8b-latest": lambda: MistralTranslationService(model_name = "ministral-8b-latest", temperature=args.temperature),
        "mistral-large-latest": lambda: MistralTranslationService(model_name = "mistral-large-latest", temperature=args.temperature),
        "mistral-medium-latest": lambda: MistralTranslationService(model_name = "mistral-medium-latest", temperature=args.temperature),
        "mistral-small-latest": lambda: MistralTranslationService(model_name = "mistral-small-latest", temperature=args.temperature),
        "mistral-tiny-latest": lambda: MistralTranslationService(model_name = "mistral-tiny-latest", temperature=args.temperature),
        "open-mistral-nemo": lambda: MistralTranslationService(model_name = "open-mistral-nemo", temperature=args.temperature),
        "open-mixtral-8x22b": lambda: MistralTranslationService(model_name = "open-mixtral-8x22b", temperature=args.temperature),
    }


    secondary_translation_service = secondary_translation_services_mapping[args.secondary_translation]()

    # Choose the secondary translation strategy.
    if args.secondary_strategy == "individual":
        from modules.secondary_translation_strategies import IndividualLabelStrategy as SecondaryStrategy
    elif args.secondary_strategy == "batch":
        from modules.secondary_translation_strategies import BatchLabelStrategy as SecondaryStrategy
    elif args.secondary_strategy == "hierarchy":
        from modules.secondary_translation_strategies import HierarchyStrategy as SecondaryStrategy
    else:
        raise ValueError(f"Invalid secondary strategy: {args.secondary_strategy}. Expected one of ['individual', 'batch', 'hierarchy'].")
    secondary_strategy = SecondaryStrategy()
    # Create an instance of the confidence calculator.
    primary_confidence_calculator = FrequencyConfidenceCalculator(logger=logger)
    if args.secondary_translation == "dummy":
        secondary_confidence_calculator = DummySecondaryConfidenceCalculator(secondary_translation_service, max_retries=args.max_retries, logger=logger)
    else:
        secondary_confidence_calculator = LLMConfidenceCalculator(secondary_translation_service, max_retries=args.max_retries, logger=logger)


    # Create and run the translation pipeline.

    pipeline = TranslationPipeline(
        primary_translation_services, 
        secondary_translation_service,
        secondary_strategy, 
        primary_confidence_calculator=primary_confidence_calculator, 
        secondary_confidence_calculator=secondary_confidence_calculator, 
        low_confidence_threshold=args.threshold, 
        min_primary_translations=args.min_primary_translations,
        logger=logger
    )

    if DEBUG == "True":
        # put all var values into the filename for debugging
        input_file = args.input
        stem, suffix = input_file.rsplit(".", 1)
        output_file = f"{stem}__{args.language}_{args.threshold}_{args.primary_translation}_{args.secondary_translation}_{args.secondary_strategy}_{args.temperature}_{start_time_str}.{suffix}"
    else:
        # output filename will be input filename with _updated as suffix
        output_file = "default"



    pipeline.process_file(input_file=args.input, target_lang=args.language, user_context=args.context, output_file=output_file)

    end_time = datetime.now()
    total_runtime = end_time - start_time
    if logger:
        logger.info(f"Script finished at {end_time}")
        logger.info(f"Total running time: {total_runtime}")

if __name__ == "__main__":
    main()
