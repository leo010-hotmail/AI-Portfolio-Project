import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chat(messages):
    """
    Sends messages to the LLM and returns the assistant reply.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.2
    )
    return response.choices[0].message.content
