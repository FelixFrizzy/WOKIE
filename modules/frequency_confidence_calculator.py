# frequency_confidence_calculator.py
from collections import defaultdict
from typing import Dict, Tuple

class FrequencyConfidenceCalculator():

    def calculate(self, translations: dict, logger=None) ->tuple[str, float]:
        """find most common translation in a collection
        More complex approach because the search needs to be case insensitive, 
        but the return should be in the original case.
        """
        if not translations:
            return None, 0.0
        count_dict = defaultdict(int)
        original_case_dict: Dict[str,str] = {}
        total_candidates = 0
        for lang, words in translations.items():
            # Ensure words is list and not a string
            if isinstance(words, str):
                words = [words]
            for word in words:
                lower_word = word.lower()
                count_dict[lower_word] += 1
                if lower_word not in original_case_dict:
                    original_case_dict[lower_word] = word
                total_candidates += 1

        most_common_lower = max(count_dict, key=count_dict.get)
        best_translation = original_case_dict[most_common_lower]
        """
        Confidence is defined as the frequency of the most common translation divided by
        the total number of translations.
        """
        confidence = count_dict[most_common_lower] / total_candidates
        return best_translation, confidence
