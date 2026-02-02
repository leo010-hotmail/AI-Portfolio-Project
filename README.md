AI Investment Assistant

AI Investment Assistant is an interactive web application that allows users to simulate stock trades using natural language. The assistant interprets user input, extracts trade parameters, and guides the user through completing the trade with contextual prompts.

Built with Streamlit and OpenAI GPT-4, this project demonstrates AI integration, conversational flows, and a dynamic trade execution interface.

Features

Natural Language Trade Input: Users can type commands like “Buy 10 shares of Apple at market price” or “I want to trade Microsoft stocks”.

Dynamic Slot Filling: The assistant asks only for missing fields such as action, quantity, price, account, and order type.

Order Types: Supports Market and Limit orders. Automatically detects order type based on user input.

Trade Summary: Shows a detailed trade summary before confirmation.

Simulated Execution: Trades are simulated for demonstration purposes.

Extensible LLM Backend: Uses OpenAI GPT-4 for parsing user input, which can be extended to other trading operations.

Tech Stack

Frontend / UI: Streamlit

AI/NLP: OpenAI GPT-4 API

Backend Logic: Python, modular structure (orchestration, services, llm)

Version Control: Git & GitHub

Getting Started
Prerequisites

Python 3.10+

OpenAI API key

Streamlit

Installation

Clone the repository:

git clone https://github.com/leo010-hotmail/AI-Portfolio-Project.git
cd AI-Portfolio-Project


Create a virtual environment and install dependencies:

python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt


Set your OpenAI API key as an environment variable:

# Windows
setx OPENAI_API_KEY "your_api_key_here"

# Mac/Linux
export OPENAI_API_KEY="your_api_key_here"


Run the app:

streamlit run app.py

Folder Structure
AI-Portfolio-Project/
│
├─ llm/                # Language model interface
├─ orchestration/      # Trade flow and orchestrator
├─ services/           # Trade service and business logic
├─ data/               # Optional datasets
├─ documentation/      # Screenshots, flow diagrams, etc.
├─ app.py              # Streamlit entry point
├─ requirements.txt    # Python dependencies

Usage

Open the app in your browser.

Type your trading instruction (e.g., “I want to buy 5 shares of Tesla”).

Follow the prompts for missing fields.

Review the trade summary and confirm.

Future Enhancements

Add audit logging for all trades.

Add GUI buttons for selecting fields like action, account, and order type.

Integrate with a real broker API for live trading (demo only for now).

Add historical portfolio insights and analytics.

License

MIT License © 2026 Aman Akbar
