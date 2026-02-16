import os
from datetime import datetime, timedelta
from typing import Iterable, List

import requests


class NewsAPIError(Exception):
    pass


PERIGON_API_URL = os.environ.get(
    "PERIGON_API_URL", "https://api.perigon.io/v1/articles/all"
)
PERIGON_API_KEY = os.environ.get("PERIGON_API_KEY") or os.environ.get("NEWS_API_KEY")

DEFAULT_LIMIT = 5
RECENT_DAYS = 10


def _validate_api_credentials():
    if not PERIGON_API_KEY:
        raise NewsAPIError("News API key is not configured (set PERIGON_API_KEY).")


def _build_query(query: str | Iterable[str]) -> str:
    if isinstance(query, str):
        return query.strip()
    return " OR ".join(str(part).strip() for part in query if part)


def fetch_news_articles(
    query: str | Iterable[str],
    limit: int = DEFAULT_LIMIT,
    *,
    company_symbol: str | None = None,
    company_name: str | None = None,
) -> List[dict]:
    _validate_api_credentials()
    normalized = _build_query(query)
    if not normalized:
        raise NewsAPIError("Provide at least one keyword or ticker to search for.")

    today = datetime.utcnow().date()
    start_date = today - timedelta(days=RECENT_DAYS)
    search_parts = [normalized]
    if company_symbol:
        search_parts.append(company_symbol)
    if company_name:
        search_parts.append(company_name)

    final_query = " ".join(dict.fromkeys(part for part in search_parts if part))

    params = {
        "apiKey": PERIGON_API_KEY,
        "pageSize": min(limit, 20),
        "sortBy": "date",
        "sourceGroup": "top25finance",
        "categories": "Business,Finance",
        "language": "en",
        "showNumResults": "true",
        "showReprints": "false",
        "startDate": start_date.isoformat(),
        "endDate": today.isoformat(),
        "size": min(limit, 20),
        "page": 0,
    }

    if company_symbol:
        params["companySymbol"] = company_symbol
        params.pop("q", None)
    elif company_name:
        params["companyName"] = company_name
        params.pop("q", None)
    else:
        params["q"] = normalized


    try:
        response = requests.get(PERIGON_API_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise NewsAPIError(f"News API request failed: {str(exc)}") from exc

    payload = response.json()
    articles = payload.get("articles") or payload.get("data") or []

    if not isinstance(articles, list):
        raise NewsAPIError("Unexpected news payload from Perigon API.")

    return articles[:limit]
