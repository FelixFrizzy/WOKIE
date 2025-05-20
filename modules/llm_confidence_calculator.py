# LLM_confidence_calculator.py
import logging
from langcodes import Language
import re
import ollama 
from rdflib import Literal

class LLMConfidenceCalculator():
    """
    Confidence calculator that uses an LLM to select the best translation and assign a confidence score.

    This class expects the following inputs:
      - context_info: a string containing the labels and descriptions in all available languages.
      - target_language: the target language code (e.g., "en").

    The class uses the secondary translation service that was set in the pipeline (via argparse).

    """
    def __init__(self, secondary_translation_service, max_retries, logger=None):
        """
        secondary_translation_service: an instance of a SecondaryTranslationService (e.g., an instance of OpenAITranslationService or OllamaTranslationService)
        """
        self.secondary_translation_service = secondary_translation_service
        self.max_retries = max_retries
        self.logger: logging.Logger = logger or logging.getLogger(__name__)
        self.service_name = "llmconfidencecalculator"

    def get_label_and_lang(self, label):
        """
        Returns a tuple (text, src_lang) from a label (either an rdflib Literal or a (text, src_lang) tuple).
        """
        if isinstance(label, tuple):
            return label
        elif hasattr(label, "language"):
            return (str(label), label.language if label.language else "en-US")
        else:
            return (str(label), "en-US")

    def get_term_descriptions(self, term_props):
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

    def choose_term_context(self, term_descriptions, src_lang):
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
    
    def compile_translations(self, primary, secondary):
        """
        Extract all strings from two translation vars (str, dict[str,str], or dict[str,list[str]]).
        deduplicated with using a set, and return as a list.
        """
        def extract_strings(data):
            # handle None values or None input
            if data is None:
                return set()
            if isinstance(data, str):
                return {data}

            if isinstance(data, dict):
                result = set()
                for v in data.values():
                    if v is None:
                        continue
                    # single string
                    if isinstance(v, str):
                        result.add(v)

                    # list of strings
                    elif isinstance(v, list):
                        for item in v:
                            if isinstance(item, str):
                                result.add(item)
                            else:
                                raise TypeError(f"List items must be str, got {type(item)}")
                            
                    else:
                        print(f"Skipping unexpected value: {v} (type: {type(v)})")
                        continue
                return result

            # anything else is an error
            raise TypeError(f"Supported types are str or dict, got {type(data)}")

        # union the two sets and return as a list
        return list(extract_strings(primary) | extract_strings(secondary))
    

    def build_prompt(self, labels: list, translation_candidates, term_descriptions, vocab_context, user_context, target_lang_full):
        instruction_prompt = """
        You are a professional translation review system that assesses the quality of translations of a single term given in different source languages. The translations are already given by a translation system. Give me the best fitting translation out of the given list and a confidence how sure you are that the translation is accurate on a scale from 0 to 1. If no possible translation seems to be fitting, return None as best fitting translation and a confidence of 0.
        Criteria for high accuracy are:
        - The best fitting translation is already found in the already given possible translations.
        - In the current context, there is no possible translation that has a different meaning.

        Only give me the best fitting translation and the confidence in this format:
        best fitting translation; confidence
        Return only the best fitting translation and confidence.

        """

        prompt = {}
        labels_str = "\n".join(labels)
        translation_candidates_str = "\n".join(translation_candidates)

        if term_descriptions:
            desc_lines = []
            for desc in term_descriptions:
                if isinstance(desc, tuple) and isinstance(desc[0], Literal):
                    literal, lang = desc
                    # literal.value would also work if you want the Python-native value
                    desc_lines.append(f"{str(literal)} ({lang})")
                else:
                    desc_lines.append(str(desc))
            term_descriptions_str = "\n".join(desc_lines)
        else:
            term_descriptions_str = None


        input_prompt = ""
        input_prompt += f"Choose the best fitting translation to {target_lang_full}. The source term given in different languages is: \n"
        input_prompt += labels_str + "\n\n"
        input_prompt += f"The possible translations to {target_lang_full} coming from translation systems are: \n"
        input_prompt += translation_candidates_str + "\n\n"
        if term_descriptions_str:
            input_prompt += f"Term descriptions are: \n"
            input_prompt += term_descriptions_str + "\n\n"
        elif vocab_context:
            input_prompt += f"Additional context is: \n"
            input_prompt += vocab_context + "\n\n"
        else:
            input_prompt += f"Additional context is: \n"
            input_prompt += user_context + "\n\n"
        input_prompt += "Return the best fitting translation and the confidence in this format:\n" \
                "<best fitting translation>; <confidence>"
        
        prompt["instructions"] = instruction_prompt
        prompt["input"] = input_prompt
        
        
        return prompt


    def calculate(self, labels: list, primary_translations: dict, secondary_translations: dict| str, term_props, vocab_context: str | None, user_context: str, target_lang: str, logger=None):
        logger = logger or self.logger
        # Build the instructions and input prompts using the provided data.
        target_lang_full = Language.make(language=target_lang).display_name()

        term_descriptions = self.get_term_descriptions(term_props)
        for label in labels:
            label_text, src_lang = self.get_label_and_lang(label)  #TODO consider error if language missing.
            term_context = self.choose_term_context(term_descriptions, src_lang)
            src_lang_full = Language.make(language=src_lang).display_name()
            target_lang_full = Language.make(language=target_lang).display_name()
        
        # The compiled translations consist of the primary and secondary translations, deduplicated.
        translation_candidates = self.compile_translations(primary_translations, secondary_translations)

        # Call the LLM with context_info being only the primary translations including language tags
        best_translation, confidence = self._call_llm(labels, translation_candidates, term_descriptions, vocab_context, user_context, target_lang_full, logger=logger)


        return best_translation, confidence



    def _call_llm(self, labels: list[str], translation_candidates, term_descriptions, vocab_context, user_context, target_lang_full, logger=None):
        """
        Calls the LLM using the secondary translation service that was set in the pipeline.
        If the response does not comply with the requested format, try again until max_retries is reached
        
        prompt: The prompt string built above.
        The LLM's output as a string.
        """

        logger = logger or self.logger
        # TODO think about if it makes sense to use .lower()
        prompt = self.build_prompt(labels, translation_candidates, term_descriptions, vocab_context, user_context, target_lang_full)

        for attempt in range(self.max_retries + 1):
            if logger:
                logger.debug(f"LLM call attempt {attempt+1}")

            response = self.secondary_translation_service.rate_translation(prompt)

            if not isinstance(response, str):
                if logger:
                    logger.warning("LLM returned None or non-string response; skipping this attempt.")
                continue
            response = response.strip()
            
            # Validate response using regex: capture everything before the first semicolon as translation,
            # and the first number (integer or decimal) as rating.
            pattern = r'^\s*(.*?)\s*;\s*([0-9]+(?:\.[0-9]+)?)'
            match = re.search(pattern, response, flags=re.MULTILINE)
            if match:
                # choose translation from re match, and remove any additional '' or whitespaces
                best_translation = match.group(1).strip().strip("'") if isinstance(match.group(1), str) else match.group(1)
                confidence = float(match.group(2).strip().strip("'")) if isinstance(match.group(2), str) else float(match.group(2))
                if translation_candidates and best_translation.lower() not in [translation_candidate.lower() for translation_candidate in translation_candidates]:
                    if logger:
                        logger.info(f"Best translation '{best_translation}' not found in primary_translations; retrying...")
                    continue  

                if 0.0 <= confidence <= 1.0:
                    return best_translation, confidence
    


        if logger:
            logger.info("LLM did not return a valid response after maximum retries, falling back to primary confidence calculator.")
            logger.debug(f"LLM reponse of last try: \n{response}")
        return None, None
    

 

