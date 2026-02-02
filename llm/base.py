from abc import ABC, abstractmethod

class LLMClient(ABC):

    @abstractmethod
    def classify_intent(self, user_input: str) -> dict:
        pass

    @abstractmethod
    def parse(self, user_input: str) -> dict:
        """
        Returns structured trade parameters.
        """
        pass
