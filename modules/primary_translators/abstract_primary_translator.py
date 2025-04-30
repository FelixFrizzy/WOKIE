from abc import ABC, abstractmethod
from typing import Optional
# ---------------------------
# Primary Translation Service Classes for use with traditional translate APIs and alike
# ---------------------------

class PrimaryTranslationService(ABC):
    """
    Abstract base class for primary translation services.
    Must implement a simple translate() method.
    """
    @abstractmethod
    def translate(self, term: str, source_lang: str, target_lang: str) -> Optional[str]:
        raise NotImplementedError("translate() must be implemented by subclasses.")