from abc import ABC, abstractmethod
from typing import List

class PromptComponent(ABC):
    @abstractmethod
    def get_text(self) -> str:
        """Return the text for this component."""
        pass

class TermLabelsComponent(PromptComponent):
    def __init__(self, labels: str):
        self.labels = labels
    def get_text(self) -> str:
        return f"Term to translate: {self.labels}"

class TermDescriptionComponent(PromptComponent):
    def __init__(self, description: str):
        self.description = description  # e.g., "A brief description of the term"
    def get_text(self) -> str:
        return f"Description of the term that should be translated: {self.description}"

class GeneralContextComponent(PromptComponent):
    def __init__(self, general_context: str):
        self.general_context = general_context
    def get_text(self) -> str:
        return f"General context of the term that should be translated: {self.general_context}"

class BroaderChainComponent(PromptComponent):
    def __init__(self, chain: str):
        self.chain = chain  # e.g., "TopTerm > MiddleTerm > CurrentTerm"
    def get_text(self) -> str:
        return f"This chain represents the hierarchy of terms, starting with the highest-level term and progressing through intermediate terms to the current term which is the one that should be translated. It defines the context of the term. {self.chain}"

class GenericComponent(PromptComponent):
    def __init__(self, text: str):
        self.text = text
    def get_text(self) -> str:
        return f"{self.text}"


class PromptComposer:
    """ Puts all relevant components of the vocabulary together"""
    def __init__(self, components: List[PromptComponent]):
        self.components = components

    def compose(self) -> str:
        # Join the text from all components with a newline
        # Ignore empty components
        return f"\n".join(comp.get_text() for comp in self.components if comp.get_text().strip())
    
