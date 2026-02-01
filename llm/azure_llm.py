from llm.base import LLMClient

class AzureOpenAILLM(LLMClient):
    def __init__(self):
        raise NotImplementedError(
            "Azure OpenAI not configured yet. "
            "This class demonstrates provider swap capability."
        )

    def classify_intent(self, user_input: str) -> dict:
        pass
