from llm.base import LLMClient

class MockLLM(LLMClient):
    def classify_intent(self, user_input: str) -> dict:
        text = user_input.lower()

        market_data_keywords = ("market data", "price of", "current price", "show me the price", "quote", "what's the price", "how is")
        if any(keyword in text for keyword in market_data_keywords) and "buy" not in text and "sell" not in text:
            return {"intent": "market_data", "confidence": 0.7}

        if "cancel" in text:
            return {"intent": "cancel_order", "confidence": 0.6}

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

        parsed = {
            "symbol": None,
            "quantity": None,
            "price": None,
            "action": None,
            "order_type": None,
            "account": None,
            "order_id": None
        }

        if "buy" in text:
            parsed.update({
                "symbol": "AAPL" if "apple" in text else "AAPL",
                "quantity": 10,
                "action": "buy"
            })

        if "sell" in text:
            parsed.update({
                "symbol": "TSLA" if "tesla" in text else "TSLA",
                "quantity": 5,
                "action": "sell"
            })

        if "cancel" in text:
            parsed["order_id"] = "test-order-123"

        clean_words = [
            token.strip(".,? ").upper()
            for token in text.split()
            if token.strip(".,? ")
        ]
        for token in clean_words:
            if token.isalpha() and 1 < len(token) <= 5:
                parsed["symbol"] = token
                break

        return parsed
