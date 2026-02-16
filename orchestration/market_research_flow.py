import re

import streamlit as st

from llm import get_llm_client
from services.news_service import NewsAPIError, fetch_news_articles


llm = get_llm_client()


def _extract_symbol(text: str) -> str | None:
    if not text:
        return None

    match = re.search(r"\$([A-Za-z]{1,5})\b", text)
    if match:
        return match.group(1).upper()

    tokens = re.findall(r"\b([A-Za-z]{2,5})\b", text)
    upper_tokens = [token for token in tokens if token.isupper()]
    return upper_tokens[0] if upper_tokens else None


def _derive_search_query(user_input: str) -> str:
    query_text = (user_input or "").strip()
    symbol = _extract_symbol(query_text)
    if symbol:
        return f"{symbol} stock news"
    if query_text:
        return query_text
    return "market news"


def _format_sources(articles: list[dict]) -> list[str]:
    lines = []
    for idx, article in enumerate(articles, start=1):
        title = article.get("title") or "Untitled"
        source = article.get("source", {}).get("name") or article.get("source_name") or "Unknown source"
        published = article.get("relevancy") or article.get("relevancy") or "Unknown date"
        url = article.get("url") or article.get("link")
        if url:
            lines.append(f"{idx}. [{title}]({url}) — {source} ({published})")
        else:
            lines.append(f"{idx}. {title} — {source} ({published})")
    return lines


def handle_market_research_flow(user_input: str):
    query = _derive_search_query(user_input)
    try:
        articles = fetch_news_articles(query, limit=5)
    except NewsAPIError as exc:
        st.session_state.trade_state = {}
        return f"Sorry, I couldn't load news right now. {str(exc)}"

    if not articles:
        st.session_state.trade_state = {}
        return f"I couldn't find any news for \"{query}\". Try another symbol or topic."

    try:
        summary = llm.summarize_articles(articles, query)
    except Exception as exc:
        st.session_state.trade_state = {}
        return f"I couldn't summarize the articles right now. {str(exc)}"

    source_lines = _format_sources(articles)

    st.session_state.trade_state = {}
    lines = [
        f"### Market Research — {query}",
        "",
        summary,
        "",
        "**Sources:**",
    ]
    lines.extend(source_lines)
    lines.append("")
    lines.append("Let me know if you want to see news about any other company.")

    return "\n".join(lines).strip()
