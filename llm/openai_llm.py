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
- portfolio_insight
- place_trade
- transfer
- kyc
- unknown

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
        
    def extract_trade_parameters(self, user_input: str) -> dict:
        system_prompt = """
    You extract structured trade instructions for a trading platform.

    Return JSON ONLY in this format:
    {
    "symbol": string | null,
    "quantity": number | null,
    "price": number | null,
    "action": "buy" | "sell" | null,
    "order_type": "market" | "limit" | null,
    "account": "cash" | "tfsa" | "rrsp" | null
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
        except:
            return {"missing_fields": ["unknown_error"]}

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
"account": "cash" | "tfsa" | "rrsp" | null
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
        for field in ["action", "symbol", "quantity", "price", "account"]:
            llm_output.setdefault(field, None)

        return llm_output