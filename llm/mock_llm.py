from llm.base import LLMClient

class MockLLM(LLMClient):
    def classify_intent(self, user_input: str) -> dict:
        text = user_input.lower()

        if "buy" in text or "sell" in text:
            return {"intent": "place_trade", "confidence": 0.6}
        if "transfer" in text:
            return {"intent": "transfer", "confidence": 0.6}
        if "address" in text or "kyc" in text:
            return {"intent": "kyc", "confidence": 0.6}
        if "portfolio" in text or "performance" in text:
            return {"intent": "portfolio_insight", "confidence": 0.6}

        return {"intent": "unknown", "confidence": 0.3}
    
    def extract_trade_parameters(self, user_input: str) -> dict:
        return {
            "symbol": "AAPL",
            "quantity": 10,
            "price": 100,
            "side": "buy",
            "account": "cash",
            "missing_fields": []
    }

    def parse(self, user_input: str) -> dict:
        text = user_input.lower()

        if "buy" in text:
            return {
                "intent": "place_trade",
                "symbol": "AAPL" if "apple" in text else None,
                "quantity": None,
                "price": None,
                "account": None
            }

        return {"intent": "unknown"}