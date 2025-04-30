import os
import pytest
import rdflib
from rdflib.compare import to_isomorphic
from rdflib import Graph


from modules.translation_pipeline import TranslationPipeline
from modules.secondary_translation_strategies import IndividualLabelStrategy
from modules.frequency_confidence_calculator import FrequencyConfidenceCalculator
from modules.llm_confidence_calculator import LLMConfidenceCalculator

# Use dummy translation services for testing

class DummyPrimaryTranslationService:
    """
    A dummy translation service for testing purposes.
    """
    def translate(self, term: str, source_lang: str, target_lang: str) -> str:
        # Dummy behavior: simply append the target language code.
        return f"{term}_{target_lang}_dummy"

class DummySecondaryTranslationService:
    def __init__(self):
        self.service_name = "dummy"
        self.model_name = "dummy_model"

    def translate_with_context(self, prompt: dict) -> str:
        label = None

        if isinstance(prompt, dict):
            # Handle dict-based prompt (e.g., OpenAI-style)
            label = prompt.get("input", "").strip()
            for line in label.splitlines():
                if line.startswith("Term to translate:"):
                    label = line.split(":", 1)[1].strip()
                    break
        else:
            raise ValueError(f"Prompt must be a dictionary containing 'instructions' and 'input' keys, but is of type {type(prompt)} with content {prompt}.")

        if not label:
            raise ValueError("Could not extract term label from prompt.")

        # Dummy output: simulate translation
        return f"{label}_dummy_fallback"
    
    rate_translation = translate_with_context

# Ensure tests work from any location.
BASE_DIR = os.path.dirname(__file__)  

def graphs_are_equal(g1, g2):
    """Check if two RDF graphs are equal, ignoring blank nodes."""
    iso1 = to_isomorphic(g1)
    iso2 = to_isomorphic(g2)
    return iso1 == iso2

# List of tuples for testing multiple files: (test_input, expected_output)
test_data = [
    (
        os.path.join(BASE_DIR, 'test_data/test_tadirah_converted_small_noen.rdf'),
        os.path.join(BASE_DIR, 'test_data/test_tadirah_converted_small_noen_updated_expected.rdf')
    ),
    # Add more test cases as needed.
]

@pytest.mark.parametrize("test_input, test_output_expected", test_data)
def test_translation_pipeline(test_input, test_output_expected):
    """Integration test to check if the SKOS translation pipeline works correctly."""
    # Derive the actual output file path.
    actual_test_output = test_input.replace('.rdf', '_updated.rdf')
    target_language = "en"
    context = "Digital Humanities"
    low_conf_threshold = 0.5
    max_retries = 0
    min_primary_translations = 3    


    primary_translation_services = []

    service_instance = DummyPrimaryTranslationService()
    primary_translation_services.append(service_instance)



    # Use dummy translation services.

    
    secondary_translation_service = DummySecondaryTranslationService()

    # Choose the secondary translation strategy (here, IndividualLabelStrategy).
    secondary_strategy = IndividualLabelStrategy()

    primary_confidence_calculator = FrequencyConfidenceCalculator()
    secondary_confidence_calculator = LLMConfidenceCalculator(secondary_translation_service, max_retries=max_retries, logger=None )

    # Create the pipeline.
    pipeline = TranslationPipeline(
        primary_translation_services,
        secondary_translation_service,
        secondary_strategy,
        primary_confidence_calculator=primary_confidence_calculator, 
        secondary_confidence_calculator=secondary_confidence_calculator, 
        low_confidence_threshold=low_conf_threshold,
        min_primary_translations=min_primary_translations,
        logger=None  # Use current approach; logger is optional.
    )


    try:
        # Run the translation process.
        pipeline.process_file(test_input, target_language, context)


        # Parse expected and actual RDF graphs.
        expected_graph = Graph()
        actual_graph = Graph()

        expected_graph.parse(test_output_expected, format='xml')
        actual_graph.parse(actual_test_output, format='xml')
        
        # Assert that the graphs are semantically equal.
        assert graphs_are_equal(expected_graph, actual_graph), "The RDF graphs are not semantically equal."
    finally:
        # pass
        # Clean up the generated output file.
        if os.path.exists(actual_test_output):
            os.remove(actual_test_output)
