# abstract_secondary_translator.py
from abc import ABC, abstractmethod
from typing import Optional, Any
# ---------------------------
# Secondary Translation Service Classes for use with LLMs and alike
# ---------------------------
class SecondaryTranslationService(ABC):
    """
    Abstract base class for fallback translation services.
    Does not inherit from TranslationService because implementation of translate method should not be enforced
    """
    @abstractmethod
    def translate_with_context(self, prompt: Any) -> Optional[str]:
        raise NotImplementedError("translate_with_context() must be implemented by subclasses.")
    
    @abstractmethod
    def rate_translation(self, prompt: Any) -> Optional[str]:
        raise NotImplementedError("rate_translation() must be implemented by subclasses. rate_translation = translate_with_context might work instead of creating a full new method")