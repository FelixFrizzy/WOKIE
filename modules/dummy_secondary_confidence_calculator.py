class DummySecondaryConfidenceCalculator:
    """
    Just for testing and trying things out
    Always returns the first label that it got as best translation and a confidence of 1.0
    """
    def __init__(self, secondary_service=None, max_retries=0, logger=None):
        self.secondary_service = secondary_service
        self.max_retries = max_retries
        self.logger = logger

    def calculate(self, labels, primary_translations, secondary_translations, term_props, vocab_context, user_context, target_lang, logger=None):
        logger = logger or self.logger
        if not labels:
            return None, 0.0
        return f"{labels[0]}_dummy", 1.0