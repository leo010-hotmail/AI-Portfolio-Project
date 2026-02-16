import os
from typing import Iterable, List

import requests


class NewsAPIError(Exception):
    pass


NEWS_API_BASE_URL = os.environ.get(
    "NEWS_API_BASE_URL", "https://newsapi.org/v2/everything"
)
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")


DEFAULT_LANGUAGE = "en"
DEFAULT_LIMIT = 5


def _validate_api_credentials():
    if not NEWS_API_KEY:
        raise NewsAPIError("News API key is not configured (environment variable NEWS_API_KEY).")


def _build_query(query: str | Iterable[str]) -> str:
    if isinstance(query, str):
        return query.strip()
    return " OR ".join(str(part).strip() for part in query if part)


def fetch_news_articles(query: str | Iterable[str], limit: int = DEFAULT_LIMIT, *, language: str = DEFAULT_LANGUAGE) -> List[dict]:
    """
    Retrieve news articles matching the query string. The default provider is NewsAPI.org,
    but this can be pointed to any API that mimics the same parameters by overriding NEWS_API_BASE_URL.
    """
    _validate_api_credentials()
    normalized = _build_query(query)
    if not normalized:
        raise NewsAPIError("Provide at least one keyword or ticker to search for.")

    params = {
        "apiKey": NEWS_API_KEY,
        "q": normalized,
        "language": language,
        "pageSize": min(limit, 20),
        "sortBy": "relevancy",
    }

    try:
        response = requests.get(NEWS_API_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise NewsAPIError(f"News API request failed: {str(exc)}") from exc

    payload = response.json()
    if payload.get("status") != "ok":
        raise NewsAPIError(f"News API error: {payload.get('message', 'unknown error')}")

    articles = payload.get("articles") or []
    return articles[:limit]
