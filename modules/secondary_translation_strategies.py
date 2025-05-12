import rdflib
from typing import List, Dict
from langcodes import Language
from collections import defaultdict, OrderedDict
from modules.prompt_builders import PromptBuilder
from modules.prompt_components import PromptComponent, TermLabelsComponent, TermDescriptionComponent, BroaderChainComponent, GeneralContextComponent, GenericComponent

# Helper functions

def get_label_and_lang(label):
    """
    Returns a tuple (text, src_lang) from a label (either an rdflib Literal or a (text, src_lang) tuple).
    """
    if isinstance(label, tuple):
        return label
    elif hasattr(label, "language"):
        return (str(label), label.language if label.language else "en-US")
    else:
        return (str(label), "en-US")

def get_term_descriptions(term_props):
    """
    Extract term descriptions from the extracted term properties.
    Looks for 'definition' first, then 'note'.
    Returns a list of tuples (description, language).
    """
    descriptions = []
    for prop in ["definition", "note"]:
        if prop in term_props:
            for lang, values in term_props[prop].items():
                for v in values:
                    descriptions.append((v, lang))
    return descriptions

def choose_term_context(term_descriptions, src_lang):
    """
    Chooses the best term context (description) for a given source language.
    """
    for desc, lang in term_descriptions:
        if lang.lower() == src_lang.lower():
            return desc.strip() if isinstance(desc,str) else desc
    for desc, lang in term_descriptions:
        if lang.lower().startswith("en"):
            return desc.strip() if isinstance(desc,str) else desc
    if term_descriptions:
        return term_descriptions[0][0].strip() if isinstance(term_descriptions[0][0], str) else term_descriptions[0][0]
    return None

def group_labels_by_language(labels):
    """
    Groups labels by their language.
    Returns a dictionary mapping language codes to lists of label texts.
    """
    grouped = defaultdict(list)
    for label in labels:
        text, lang = get_label_and_lang(label)
        grouped[lang].append(text)
    return grouped

class BaseSecondaryTranslationStrategy:
    def translate(self, labels, graph, concept, term_props, vocab_context, user_context,
                  secondary_translation_service, target_lang, logger=None):
        """
        Abstract method to translate a list of labels.
        """
        raise NotImplementedError


class IndividualLabelStrategy(BaseSecondaryTranslationStrategy):
    """
    Returns dict with languages as key and translation as value
    Calculates the translations individually for each language tag using individual prompts.
    """
    def translate(self, labels, graph, concept, term_props, vocab_context, user_context,
                  secondary_translation_service, target_lang, logger=None):
        term_descriptions = get_term_descriptions(term_props)
        #TODO check which fiels are used for descriptions.
        #TODO decide what to do if there are definitions in multiple languages.
        translations: Dict[str,str ] = {}
        # Get the service type from the secondary translation service.
        service_name = secondary_translation_service.service_name.lower()
        for label in labels:
            label_text, src_lang = get_label_and_lang(label)  #TODO consider error if language missing.
            term_context = choose_term_context(term_descriptions, src_lang)
            src_lang_full = Language.make(language=src_lang).display_name()
            target_lang_full = Language.make(language=target_lang).display_name()
            # Build prompt components for individual strategy.
            # Include the term label and its description get included.
            components: List[PromptComponent] = [TermLabelsComponent(label_text)]
            if term_context:
                components.append(TermDescriptionComponent(term_context))
                if logger:
                    logger.debug(f"        Using term description for '{label_text}' in language '{src_lang}': {term_context}")
            elif vocab_context:
                components.append(GeneralContextComponent(vocab_context))
                if logger:
                    logger.info(f"        No term description for '{label_text}'; using vocabulary description as context: {vocab_context}")
            else:
                if logger:
                    logger.debug(f"        No term and vocabulary description for '{label_text}'; using user given description as context: {user_context}")
                components.append(GeneralContextComponent(user_context))


            # Instantiate the unified prompt builder with the components and service type.
            prompt_builder = PromptBuilder(components, service_name)
            final_prompt = prompt_builder.build_prompt(target_lang_full)
            if logger:
                logger.debug(f"        Individual strategy prompt built: {final_prompt}")
            # Call the translation service with the final prompt.
            translation = secondary_translation_service.translate_with_context(final_prompt)
            if isinstance(translation, str):
                translation = translation.strip(" \t\n\r'\"")
            translations[f"{src_lang}"] = translation
            if logger:
                logger.info(f"        Translation for '{label_text}' ({src_lang}) -> '{translation}' ({target_lang})")
        return translations

#  Batch Label Strategy 
class BatchLabelStrategy(BaseSecondaryTranslationStrategy):
    """
    Returns a single translation
    Calculates the translations using all available languages for each language tag and compiles it into a single prompt.
    """
    def translate(self, labels, graph, concept, term_props, vocab_context, user_context,
                  secondary_translation_service, target_lang, logger=None):
        term_descriptions = get_term_descriptions(term_props)
        grouped = group_labels_by_language(labels)
        sections = []
        for lang, label_list in grouped.items():
            term_context = choose_term_context(term_descriptions, lang)
            #TODO this is not thought through, pragmatic for now
            #TODO what if the language of description of the current term does not exist?
            if not term_context:
                if logger:
                    logger.info(f"        No term description for language '{lang}'; using fallback context: {vocab_context}")
            else:
                if logger:
                    logger.debug(f"        Using term description for language '{lang}': {term_context}")
            lang_full = Language.make(language=lang).display_name() if lang != "none" else "unspecified language"
            # build a section for each language
            section = f"Label (in {lang_full}) of term to translate:\n" #TODO think about also using altLabels etc
            for lab in label_list:
                section += f"- {lab}\n"
            if term_context:
                section += f"Context: {term_context}\n"
                if logger:
                    logger.debug(f"        Using term description for language'{lang}'; {term_context}")
            elif vocab_context:
                section += f"Context: {vocab_context}\n"
                if logger:
                    logger.info(f"        No term description for language '{lang}'; using vocabulary description as context: {vocab_context}")
            else:
                section += f"Context: {user_context}\n"
                if logger:
                    logger.info(f"        No term and vocabulary description for language '{lang}'; using user given description as context: {vocab_context}")
            sections.append(section)

        # Get full display name of target language
        target_lang_full = Language.make(language=target_lang).display_name()
        combined_context = "\n".join(sections)

        # Select service type.
        service_name = secondary_translation_service.service_name.lower()
        # Build prompt using the unified prompt builder.
        prompt_builder = PromptBuilder([GenericComponent(combined_context)], service_name)
        final_prompt = prompt_builder.build_prompt(target_lang_full)
        if logger:
            logger.debug(f"        Batch translation prompt built:\n{final_prompt}")
        translation: str = secondary_translation_service.translate_with_context(final_prompt)
        if isinstance(translation, str):
            translation = translation.strip(" \t\n\r'\"")
        # returns a single translation
        return translation

#  Hierarchy Strategy 
class HierarchyStrategy(BaseSecondaryTranslationStrategy):
    """
    Traverses the broader hierarchy (using skos:broader) from the current concept up in the hierarchy,
    collects the prefLabels in an ordered chain, and builds a context string.
    
    The chain is formatted (for each language seperately):
        Hierarchy (from top to bottom) for <Language Full Name> (<lang code>):
        Term1
        Term2
        Term3
        ...
    
    If separate_language_prompts is False, all language chains are combined into one prompt.
    If True, a separate prompt is built for each language and then the best translation is selected
    using the confidence calculator.
    If no broader terms are found, falls back to the IndividualLabelStrategy.
    """
    def translate(self, labels, graph, concept, term_props, vocab_context, user_context,
                  secondary_translation_service, target_lang, logger=None, separate_language_prompts=True):
        SKOS = rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")
        broaderUri = SKOS.broader

        # Fallback: if no broader term exists, fall back to IndividualLabelStrategy.
        if not list(graph.objects(concept, broaderUri)):
            if logger:
                logger.info("No broader terms found; falling back to IndividualLabelStrategy.")
            from modules.secondary_translation_strategies import IndividualLabelStrategy
            return IndividualLabelStrategy().translate(labels, graph, concept, term_props,
                                                       vocab_context, user_context, secondary_translation_service,
                                                       target_lang, logger=logger)
        if logger:
            logger.info("Broader terms found; using HierarchyStrategy.")

        # Get all available languages from the prefLabel.
        if "prefLabel" in term_props and term_props["prefLabel"]:
            available_languages = list(term_props["prefLabel"].keys())
        else:
            available_languages = ["en"]

        # If separate_language_prompts false, build a single prompt for all languages
        if not separate_language_prompts:
            #  Combine all language chains into one prompt 
            language_sections = []
            for lang in available_languages:
                chain = self._build_broader_chain(graph, concept, lang, target_lang)
                current_label = self._get_pref_label_for_concept(graph, concept, lang, target_lang)
                # Append the term that should be translated to the chain as last entry
                if current_label:
                    chain.append(current_label)
                lang_full = Language.make(language=lang).display_name()
                section_header = f"Hierarchy (from top to bottom) for {lang_full} ({lang}):"
                chain_str = section_header + "\n" + "\n".join(chain) + "\n"
                language_sections.append(chain_str)
            combined_chains = "\n".join(language_sections)
            target_lang_full = Language.make(language=target_lang).display_name()
            # TODO The term that should be translated is missing here. It should go into the prompt
            # TODO Problem: the term should go into the prompt in all available languages
            overall_header = (f"Give me a single translation to {target_lang_full}.\n"
                              "Here are the hierarchy chains for the term in different languages.\n\n")
            overall_footer = "\nReturn only the translated term."
            final_combined_prompt = overall_header + combined_chains + overall_footer

            if logger:
                logger.debug(f"Built hierarchy prompt:\n{final_combined_prompt}")

            service_name = secondary_translation_service.service_name.lower()
            prompt_builder = PromptBuilder([GenericComponent(final_combined_prompt)], service_name)
            target_lang_full = Language.make(language=target_lang).display_name()
            final_prompt = prompt_builder.build_prompt(target_lang_full)
            if logger:
                logger.debug(f"Formatted final prompt:\n{final_prompt}")

            translation = secondary_translation_service.translate_with_context(final_prompt)
            if isinstance(translation, str):
                translation = translation.strip(" \t\n\r'\"")
            # returns a single translation
            return translation
        
        # If separate_language_prompts true, build individual prompts for all languages and select best translation
        else:
            translations: Dict[str, str] = {}
            # individual_prompts = []
            for src_lang in available_languages:
                chain = self._build_broader_chain(graph, concept, src_lang, target_lang)
                current_label = self._get_pref_label_for_concept(graph, concept, src_lang, target_lang)
                if current_label:
                    chain.append(current_label)
                src_lang_full = Language.make(language=src_lang).display_name()
                target_lang_full = Language.make(language=target_lang).display_name()
                section_header = f"Hierarchy (from top to bottom with the last entry being the term that you should translate) for {src_lang_full}:"
                chain_str = section_header + "\n" + "\n".join(chain) + "\n"
                overall_header = (f"Give me a single translation of the {src_lang_full} term {current_label} to the{target_lang_full} language.\n")
                overall_footer = "\nReturn only the translated term in this format: translated term"
                prompt_text = overall_header + chain_str + overall_footer

                # Build the final prompt for this language.
                service_name = secondary_translation_service.service_name.lower()
                prompt_builder = PromptBuilder([GenericComponent(prompt_text)], service_name)
                target_lang_full = Language.make(language=target_lang).display_name()
                final_prompt = prompt_builder.build_prompt(target_lang_full)
                # individual_prompts.append(final_prompt)
                if logger:
                    logger.debug(f"        Built individual hierarchy chain prompt for language {src_lang}:\n{final_prompt}")
                
                translation = secondary_translation_service.translate_with_context(final_prompt)
                if isinstance(translation, str):
                    translation = translation.strip(" \t\n\r'\"")
                translations[f"{src_lang}"] = translation

                if logger:
                    logger.info(f"        Translation for '{current_label}' ({src_lang}) -> '{translations[f'{src_lang}']}' ({target_lang})")

            return translations

    def _get_pref_label_for_concept(self, graph, concept, desired_lang, target_lang):
        # TODO possible duplicate with functions at beginning
        prefLabelUri = rdflib.URIRef("http://www.w3.org/2004/02/skos/core#prefLabel")
        labels_list = list(graph.objects(concept, prefLabelUri))
        lang_labels = {}
        for label in labels_list:
            label_lang = label.language if label.language else "none"
            lang_labels.setdefault(label_lang, []).append(str(label))
        if desired_lang in lang_labels:
            return lang_labels[desired_lang][0]
        elif "en" in lang_labels:
            return lang_labels["en"][0]
        elif lang_labels:
            return next(iter(lang_labels.values()))[0]
        else:
            return None

    def _build_broader_chain(self, graph, concept, desired_lang, target_lang):
        # TODO possible duplicate with functions at beginning
        SKOS = rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")
        broaderUri = SKOS.broader
        chain = []
        current = concept
        while True:
            broader_list = list(graph.objects(current, broaderUri))
            if not broader_list:
                break
            broader = broader_list[0]
            label = self._get_pref_label_for_concept(graph, broader, desired_lang, target_lang)
            if not label:
                label = "[No label]"
            chain.insert(0, label)  # Insert so that the top term comes first.
            current = broader
        return chain

    def _get_term_description_for_concept(self, term_props, desired_lang, target_lang):
        # TODO possible duplicate with functions at beginning
        for prop in ["definition", "note"]:
            if prop in term_props and desired_lang in term_props[prop]:
                return str(term_props[prop][desired_lang][0])
        for fallback_lang in [target_lang, "en"]:
            for prop in ["definition", "note"]:
                if prop in term_props and fallback_lang in term_props[prop]:
                    return str(term_props[prop][fallback_lang][0])
        return None
