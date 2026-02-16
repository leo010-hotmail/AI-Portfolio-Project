from openai import OpenAI
from llm.base import LLMClient
import os
import json
import streamlit as st

class OpenAILLM:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")

        self.client = OpenAI(api_key=api_key)

    def classify_intent(self, user_input: str) -> dict:
        system_prompt = """
You are an intent classifier for a trading platform assistant.

Possible intents:
- place_trade
- cancel_order
- view_orders
- view_portfolio
- transfer
- kyc
- help_faq
- market_data
- market_research
- unknown

cancel_order: user wants to cancel an existing open order.
view_orders: user wants to view the details of all open orders.
view_portfolio: user wants to view the details of all the stocks in their account. 
market_data: user is asking for information about a particular stock such as its current price,
day high, day low, historical price, trading volume, opening price, closing price
market_research: user is asking for investment ideas, comparisons,
market trends, or research-oriented information.
help_faq: user is asking how to do something in the app or where to find information.

Return JSON ONLY in this format:
{
  "intent": "<intent>",
  "confidence": 0.0-1.0
}
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0
        )

        content = response.choices[0].message.content

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"intent": "unknown", "confidence": 0.0}


    def parse(self, user_input: str) -> dict:
            
        system_prompt = """
You are an AI assistant for a trading platform.  

Extract structured trade instructions in JSON format.  
Return **JSON ONLY** like this:

{
"symbol": string | null,
"quantity": number | null,
"price": number | null,
"action": "buy" | "sell" | null,
"order_type": "market" | "limit" | null,
"account": "cash" | "tfsa" | "rrsp" | null,
"order_id": string | null
}

Rules:
- If the user did not provide a value for a field, return null
- Do not assume defaults for missing fields
- Only parse what is explicitly mentioned by the user
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0
        )

        content = response.choices[0].message.content.strip()

        # Parse JSON safely
        try:
            llm_output = json.loads(content)
        except json.JSONDecodeError:
            # fallback in case LLM returns invalid JSON
            llm_output = {
                "symbol": None,
                "quantity": None,
                "price": None,
                "action": None,
                "account": None
            }

        # normalize keys in case older versions use 'side'
        if "side" in llm_output:
            llm_output["action"] = llm_output.pop("side")

        # ensure all required fields exist
        for field in ["action", "symbol", "quantity", "price", "order_type", "account", "order_id"]:
            llm_output.setdefault(field, None)

        return llm_output
