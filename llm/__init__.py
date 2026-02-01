import os
from llm.openai_llm import OpenAILLM
from llm.mock_llm import MockLLM

def get_llm_client():
    provider = os.getenv("LLM_PROVIDER", "openai")

    if provider == "openai":
        return OpenAILLM()
    else:
        return MockLLM()
