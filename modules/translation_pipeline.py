# translation_pipeline.py
from datetime import datetime
import rdflib
from rdflib import Literal, Namespace
from langcodes import Language
from modules.utils import temporary_setattr
from modules.skos_handler import load_graph, extract_vocabulary_context, extract_term_properties, SKOS_TERM_PROPERTIES

# --- Helper functions (copied from secondary translation strategies) ---

def get_label_and_lang(label):
    if isinstance(label, tuple):
        return label
    elif hasattr(label, "language"):
        return (str(label), label.language if label.language else "en-US")
    else:
        return (str(label), "en-US")

def get_term_descriptions(term_props):
    descriptions = []
    for prop in ["definition", "note"]:
        if prop in term_props:
            for lang, values in term_props[prop].items():
                for v in values:
                    descriptions.append((v, lang))
    return descriptions

def group_labels_by_language(labels):
    from collections import defaultdict
    grouped = defaultdict(list)
    for label in labels:
        text, lang = get_label_and_lang(label)
        grouped[lang].append(text)
    return grouped

class TranslationPipeline:
    """
    Reads a SKOS file, translates missing term properties to the target language,
    and writes the updated graph to an output file.

    #TODO only prefLabel is translated, think about if other properties (e.g. skos:definition) should also be translated

    Parameters:
      - input_file: Path to the input SKOS file (RDF/XML or Turtle)
      - target_lang: Language code for the target language.
      - primary_translation_services: A list of TranslationService instances.
      - secondary_translation_service: An instance of a SecondaryTranslationService.
      - secondary_strategy: An instance of a secondary translation strategy.
      - primary_confidence_calculator: An instance of a ConfidenceCalculator.
      - secondary_confidence_calculator: An instance of a ConfidenceCalculator.
      - confidence_calculator: An instance of a ConfidenceCalculator.
      - user_context: User-defined context.
      - low_confidence_threshold: Threshold below which secondary translation is triggered.
    """
    def __init__(self, primary_translation_services, secondary_translation_service,
                 secondary_strategy, primary_confidence_calculator, secondary_confidence_calculator, low_confidence_threshold=0.5, min_primary_translations=3, logger=None):
        self.primary_translation_services = primary_translation_services
        self.secondary_translation_service = secondary_translation_service
        self.secondary_strategy = secondary_strategy
        self.primary_confidence_calculator = primary_confidence_calculator
        self.secondary_confidence_calculator = secondary_confidence_calculator
        self.low_confidence_threshold = low_confidence_threshold
        self.min_primary_translations = min_primary_translations
        self.logger = logger

        # Define which SKOS properties to translate
        # Currently only prefLabel will be translated
        self.properties_to_translate = ["prefLabel"] #TODO translation of skos:note does of course not work with simple translation service

    # When output_file is set to "default", the string "_updated" is appended to the input_filename
    def process_file(self, input_file, target_lang, user_context, output_file="default"):
        # Load the SKOS graph and extract vocabulary-level context.
        graph, fileformat = load_graph(input_file)
        vocab_context = extract_vocabulary_context(graph)
        
        # Extract all term properties at once
        term_properties = extract_term_properties(graph)
        total_concepts = len(term_properties)
        if self.logger:
            self.logger.info(f"Total concepts: {total_concepts}")

        # Iterate over each term (concept) in the vocabulary
        for i, (concept, term_props) in enumerate(term_properties.items(), start=1):
            # Use ANSI codes (\033[K) to erase until end of line for proper flushing
            # Does not properly work when piping console output to file
            print(f"\r\033[KProcessing term {i}/{total_concepts}: {concept}", end='', flush=True)
            if self.logger:
                self.logger.info(f"Processing concept: {concept}")
            for prop_name in self.properties_to_translate:
                if prop_name not in term_props:
                    continue
                lang_dict = term_props[prop_name]
                # Skip if target language value already exists.
                if target_lang in lang_dict:
                    continue

                primary_translations = {}
                total_candidates = 0

                for service in self.primary_translation_services:
                    # Translate all available source-language labels using this service
                    for src_lang, prop_values in lang_dict.items():
                        for prop_value in prop_values:
                            if str(prop_value) == "":
                                continue 
                            translation = service.translate(prop_value, src_lang, target_lang)
                            if src_lang not in primary_translations and translation is not None:
                                primary_translations[src_lang] = []
                            if translation is not None:
                                primary_translations[src_lang].append(translation)
                                total_candidates += 1
                                if self.logger:
                                    self.logger.info(f"    Primary translation from {service.__class__.__name__} for {prop_name}: '{prop_value}' ({src_lang}) -> '{translation}' ({target_lang})")
                    # Break if enough translations are there.
                    if total_candidates >= self.min_primary_translations:
                        break                

                
                # Call the confidence calculator for primary translations.
                if total_candidates >= self.min_primary_translations:
                    best_translation, primary_confidence = self.primary_confidence_calculator.calculate(primary_translations)
                else:
                    best_translation = None
                    primary_confidence = None

                # If primary confidence is low, use secondary translation strategy.
                if primary_confidence is None or primary_confidence < self.low_confidence_threshold or best_translation is None:
                    if self.logger:
                        self.logger.info(f"    Low confidence ({primary_confidence}) for term {concept}, property {prop_name}, using secondary translation service")
                    # Aggregate all source values for this property
                    labels: list[str] = []
                    for values in lang_dict.values():
                        labels.extend(values)
                    # Pass the extracted properties for this concept as term_props.
                    # translate with secondary translation strategy
                    # depending on strategy, dict or string is returned
                    secondary_translations = self.secondary_strategy.translate(
                        labels, graph, concept, term_props, vocab_context, user_context,
                        self.secondary_translation_service, target_lang, logger=self.logger
                    )
                    # Check if the most common translation of the possible secondary translations (each translated from a different language) is in primrary translations
                    if isinstance(secondary_translations, dict):
                        most_common_secondary_translation, _ = self.primary_confidence_calculator.calculate(secondary_translations)
                    else:
                        most_common_secondary_translation = secondary_translations

                    # If most common secondary translation is in primary translations, use it as best_translation and set secondary_confidence to 1. Steps explained in the following

                    # Check every value in primary_translations (could be a str or list of str)
                    if any(
                        # Case 1: primary_translation is a string and matches our secondary (case-insensitive)
                        (isinstance(primary_translation, str) and primary_translation.lower() == most_common_secondary_translation.lower())
                        # Case 2: primary_translation is a list of strings, check each element
                        or (isinstance(primary_translation, list) and any(
                            isinstance(candidate, str) and candidate.lower() == most_common_secondary_translation.lower()
                            for candidate in primary_translation
                        ))
                        for primary_translation in primary_translations.values()
                    ):
                        # most common secondary translation is in primary translations, so choose it as best_translation
                        best_translation = most_common_secondary_translation

                        # Choose confidence of 1
                        secondary_confidence = 1


                    # If most common secondary translation is not in primary translations, use the secondary_confidence_calculator, but include the primary translations
                    else:


                        # compile a dict of all primary and secondary translations
                        # use secondary confidence calculator (LLM based) to rate the translation
                        # Temporarily set max_retries to 0 because I only want to try this once (so no retries)
                        with temporary_setattr(self.secondary_confidence_calculator, "max_retries", 0):
                            best_translation, secondary_confidence = self.secondary_confidence_calculator.calculate(labels, primary_translations, secondary_translations, term_props, vocab_context, user_context, target_lang, logger=self.logger)
                    # use primary_conficence_calculator if it fails
                    if not best_translation or not secondary_confidence:
                        best_translation, secondary_confidence = self.primary_confidence_calculator.calculate(secondary_translations)
                    if self.logger:
                        self.logger.info(f"        Secondary translation chosen for {prop_name}: '{best_translation}' with confidence {secondary_confidence}")
                # Add the best translation as a new literal for the property in the target language.
                graph.add((concept, SKOS_TERM_PROPERTIES[prop_name], Literal(best_translation, lang=target_lang)))

        # Serialize the updated graph.
        if output_file == "default":
            stem, suffix = input_file.rsplit(".", 1)
            output_file = f"{stem}_updated.{suffix}"
        else:
            output_file = output_file
        graph.serialize(destination=output_file, format=fileformat) # type: ignore
        if self.logger:
            self.logger.info(f"Updated SKOS file saved: {output_file}")
        print(f"\nUpdated SKOS file saved: {output_file}")
