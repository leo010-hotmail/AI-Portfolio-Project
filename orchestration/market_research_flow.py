from datetime import datetime

import streamlit as st

from llm import get_llm_client
from services.news_service import NewsAPIError, fetch_news_articles

llm = get_llm_client()


def _derive_search_query(user_input: str, company_details: dict) -> tuple[str, str | None, str | None]:
    query_text = (user_input or "").strip()
    symbol = company_details.get("company_symbol")
    company_name = company_details.get("company_name")

    if symbol:
        symbol_query = f"{symbol} stock news"
        return symbol_query, symbol, company_name
    if company_name:
        name_query = f"{company_name} stock news"
        return name_query, None, company_name
    if query_text:
        return query_text, None, None
    return "market news", None, None


def _format_sources(articles: list[dict]) -> list[str]:
    lines = []

    def _source_label(article: dict) -> str:
        source = article.get("source") or {}
        domain = source.get("domain")
        name = source.get("name") or article.get("source_name") or article.get("sourceName")
        if name:
            return name
        if domain:
            return domain.replace("www.", "")
        companies = article.get("companies") or []
        if companies:
            first = companies[0].get("name")
            if first:
                return first
        return "Unknown source"

    def _published_label(article: dict) -> str:
        published = (
            article.get("pubDate")
            or article.get("pubdate")
            or article.get("publishedAt")
            or article.get("published_at")
            or article.get("published")
            or article.get("date")
            or article.get("datePublished")
            or article.get("addDate")
        )
        if not published:
            return "Unknown date"
        try:
            return datetime.fromisoformat(published.rstrip("Z")).strftime("%Y-%m-%d")
        except ValueError:
            return published

    for idx, article in enumerate(articles, start=1):
        title = article.get("title") or "Untitled"
        source_label = _source_label(article)
        published = _published_label(article)
        url = article.get("url") or article.get("link")
        if url:
            lines.append(f"{idx}. [{title}]({url}) — {source_label} ({published})")
        else:
            lines.append(f"{idx}. {title} — {source_label} ({published})")

    return lines


def handle_market_research_flow(user_input: str):
    company_details = llm.extract_company_details(user_input)
    query, symbol, company_name = _derive_search_query(user_input, company_details)
    try:
        articles = fetch_news_articles(
            query, limit=5, company_symbol=symbol, company_name=company_name
        )
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
