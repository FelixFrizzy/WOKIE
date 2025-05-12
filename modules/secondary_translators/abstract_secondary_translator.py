# abstract_secondary_translator.py
from abc import ABC, abstractmethod
from typing import Optional, Any

class SecondaryTranslationService(ABC):
    """
    Abstract base class for secondary translation services.
    """
    @abstractmethod
    def translate_with_context(self, prompt: Any) -> Optional[str]:
        raise NotImplementedError("translate_with_context() must be implemented by subclasses.")
    
    @abstractmethod
    def rate_translation(self, prompt: Any) -> Optional[str]:
        raise NotImplementedError("rate_translation() must be implemented by subclasses. rate_translation = translate_with_context might work instead of creating a full new method, just try it out")