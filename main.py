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
from modules.secondary_translators.ollama_translator import OllamaTranslationService
from modules.secondary_translators.openai_translator import OpenAITranslationService
from modules.secondary_translators.deepseek_translator import DeepseekTranslationService
from modules.frequency_confidence_calculator import FrequencyConfidenceCalculator
from modules.llm_confidence_calculator import LLMConfidenceCalculator
from config import DEBUG
# from config import MAX_RETRIES, TEMPERATURE, DEBUG # TODO implement env vars correctly


def main():
    parser = argparse.ArgumentParser(description="Translate a SKOS file to the desired language")
    parser.add_argument("-i", "--input", required=True, 
                        help="Path to the source SKOS file")
    # parser.add_argument("-l", "--languages", nargs="+", default=["en"], 
    #                     help="Target languages seperated by space as IETF BCP 47 language tag for translation (e.g. de en fr).") # this will be used later when more than one language is supported #TODO

    parser.add_argument("--language", required=True, 
                        help="Target language as IETF BCP 47 tag (e.g. de)")
    parser.add_argument("--context", default="", 
                        help="Topic or Context of source vocabulary")
    parser.add_argument("--threshold", type=float, default=0.66, 
                        help="Threshold for decision if secondary translation services are used to refine translations")
    parser.add_argument("--primary_translation", required=True, nargs='+', choices=["argos", "google", "lingvanex", "microsoft", "modernmt", "mymemory", "pons", "ponspaid", "reverso", "translatecom", "yandex"], 
                        help="Primary (deterministic) translation service. Options: argos, google, lingvanex, microsoft, modernmt, mymemory, pons, ponspaid, reverso, translatecom, yandex")
    parser.add_argument("--secondary_translation", required=True, choices=["deepseek-r1:1.5b", "deepseek-chat", "deepseek-reasoner", "llama3.2", "gpt-3.5-turbo", "gpt-4o"], 
                        help="Secondary (language-model based) translation service. Options: deepseek-r1:1.5b, deepseek-chat, deepseek-reasoner, llama3.2, gpt-3.5-turbo, gpt-4o")
    parser.add_argument("--secondary_strategy", required=False, default="individual", choices=["individual", "batch", "hierarchy"],
                        help="Secondary translation strategy. Options: individual, batch, hierarchy")
    parser.add_argument("--enable-logging", action="store_true", 
                        help="Enable logging")
    args = parser.parse_args()

    # Needed number of translations of a single term before the primary confidence calculator is called
    min_primary_translations = 3
    # If the response of an LLM does not comply with the requested format, try again for <max_retries> times
    max_retries = 1
    # temperature (sth like randomness control level), between 0 and 2
    temperature = 0


    logger = None
    if args.enable_logging:
        # Setup logging: the log file will be in the same folder as this main script.
        dirname, basename = os.path.split(args.input)
        basename = basename.split(".")[0]
        # last_folder = os.path.basename(dirname)
        # log_file = os.path.join(os.path.dirname(__file__), f"translation_{last_folder}_{basename}_{args.language}_{args.secondary_strategy}.log")
        # Store log file in folder of main.py
        # log_file = os.path.join(os.path.dirname(__file__), f"log_{basename}__{args.language}_{args.threshold}_{args.primary_translation}_{args.secondary_translation}_{args.secondary_strategy}_{temperature}.log")
        # Store log file in folder of input file
        log_file = os.path.join(dirname, f"log_{basename}__{args.language}_{args.threshold}_{args.primary_translation}_{args.secondary_translation}_{args.secondary_strategy}_{temperature}.log")

        "log_defc_nola__la_individual.log"


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

    start_time = datetime.now()
    if logger:
        logger.info(f"Script started at {start_time}")
        logger.info(f"Input file: {args.input}")
        logger.info(f"Target language: {args.language}")
        logger.info(f"Primary translation service: {args.primary_translation}")
        logger.info(f"Secondary translation services: {args.secondary_translation}")
        logger.info(f"Secondary translation strategy: {args.secondary_strategy}")
        logger.info(f"User provided context: {args.context}")
        logger.info(f"Max. retries for secondary confidence calculator: {max_retries}")
        logger.info(f"Temperature for secondary confidence calculator: {temperature}")
        logger.info(f"Minimal number of primary translations before calling primary confidence calculator: {min_primary_translations}")
        logger.info(f"Threshold: {args.threshold}")

    # Dictionary for mapping secondary service names to their respective classes
    primary_translation_services_mapping = {
        "argos": ArgosTranslationService, 
        "google": GoogleTranslationService,
        "lingvanex": LingvanexTranslationService, 
        "modernmt": ModernMTTranslationService,  
        "microsoft": MicrosoftTranslationService,  
        "mymemory": MyMemoryTranslationService,  
        "pons": PonsTranslationService,  
        "ponspaid": PonsPaidTranslationService,  
        "reverso": ReversoTranslationService,  
        "translatecom": TranslatecomTranslationService,  
        "yandex": YandexTranslationService
    }

    primary_translation_services = []
    for service_name in args.primary_translation:
        try:
            service_class = primary_translation_services_mapping[service_name]
        except KeyError:
            raise ValueError(f"Primary translation service {service_name} is currently not implemented")
        
        service_instance = service_class()
        primary_translation_services.append(service_instance)
        if logger:
            logger.info(f"Primary translation service {service_name} instantiated successfully")

    if logger:
        chosen_services = ", ".join(args.primary_translation)
        logger.info(f"Order of primary translation services (first in list used first in translations): {chosen_services}")


    # Dictionary for mapping secondary service names to their respective classes
    # Use lambda to delay execution because certain Translation services requires args.model which is not present at dict initialization. Also avoid unneccesary object creation
    secondary_translation_services_mapping = {
        "deepseek-r1:1.5b": lambda: OllamaTranslationService(model_name="deepseek-r1:1.5b"), 
        "deepseek-chat": lambda: DeepseekTranslationService(model_name="deepseek-chat"), 
        "deepseek-reasoner": lambda: DeepseekTranslationService(model_name="deepseek-reasoner"), 
        "llama3.2": lambda: OllamaTranslationService(model_name="llama3.2"), 
        "gpt-3.5-turbo": lambda: OpenAITranslationService(model_name="gpt-3.5-turbo", temperature = temperature),
        "gpt-4o": lambda: OpenAITranslationService(model_name="gpt-4o", temperature = temperature)
    }


    secondary_translation_service = secondary_translation_services_mapping[args.secondary_translation]()
    # Add an attribute so strategies know which service is used.
    # secondary_translation_service.service_name = args.secondary_translation

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
    primary_confidence_calculator = FrequencyConfidenceCalculator()
    secondary_confidence_calculator = LLMConfidenceCalculator(secondary_translation_service, max_retries=max_retries, logger=logger)


    # Create and run the translation pipeline.

    pipeline = TranslationPipeline(
        primary_translation_services, 
        secondary_translation_service,
        secondary_strategy, 
        primary_confidence_calculator=primary_confidence_calculator, 
        secondary_confidence_calculator=secondary_confidence_calculator, 
        low_confidence_threshold=args.threshold, 
        min_primary_translations=min_primary_translations,
        logger=logger
    )

    if DEBUG == "True":
        input_file = args.input
        stem, suffix = input_file.rsplit(".", 1)
        output_file = f"{stem}__{args.language}_{args.threshold}_{args.primary_translation}_{args.secondary_translation}_{args.secondary_strategy}_{temperature}.{suffix}"
    else:
        output_file = "default"


    # TODO set this to default and comment out output file naming logic from above
    # output_file = "default"

    pipeline.process_file(input_file=args.input, target_lang=args.language, user_context=args.context, output_file=output_file)

    end_time = datetime.now()
    total_runtime = end_time - start_time
    if logger:
        logger.info(f"Script finished at {end_time}")
        logger.info(f"Total running time: {total_runtime}")

if __name__ == "__main__":
    main()
