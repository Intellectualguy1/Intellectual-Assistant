from config import SEARCH_PROVIDER, TAVILY_API_KEY


def fix_encoding(text: str) -> str:
    """
    Fixes common mojibake encoding issues in web result titles/content.

    Example:
    - ÃlysÃ©e -> Élysée
    - PrÃ©sidence -> Présidence
    - RÃ©publique -> République

    Time Complexity:
    - O(n), where n is the length of the text.
    """
    if not text:
        return ""

    fixed = text

    try:
        if "Ã" in fixed or "Â" in fixed:
            fixed = fixed.encode("latin1").decode("utf-8")
    except UnicodeError:
        pass

    replacements = {
        "ÃlysÃ©e": "Élysée",
        "Ãlysée": "Élysée",
        "Ã‰lysÃ©e": "Élysée",
        "Ã‰lysée": "Élysée",
        "PrÃ©sidence": "Présidence",
        "RÃ©publique": "République",
        "Ã©": "é",
        "Ã¨": "è",
        "Ãª": "ê",
        "Ã«": "ë",
        "Ã ": "à",
        "Ã¢": "â",
        "Ã´": "ô",
        "Ã»": "û",
        "Ã¹": "ù",
        "Ã§": "ç",
        "Â": "",
    }

    for wrong, correct in replacements.items():
        fixed = fixed.replace(wrong, correct)

    return fixed


def clean_text(text: str, max_length: int = 500) -> str:
    """
    Cleans and limits long search result text.

    Time Complexity:
    - O(n), where n is the length of the text.
    """
    if not text:
        return ""

    fixed = fix_encoding(text)
    cleaned = " ".join(fixed.split())

    if len(cleaned) > max_length:
        return cleaned[:max_length].strip() + "..."

    return cleaned


def mock_search(query: str):
    """
    Mock web search provider.

    Time Complexity:
    - O(1), because it returns a fixed list of results.
    """

    return [
        {
            "title": "Mock Search Result - Intellectual Assistant",
            "url": "https://github.com/",
            "snippet": (
                "This is a mock web search result. "
                "In the next stage, Intellectual Assistant will fetch real-time web results."
            )
        }
    ]


def tavily_search(query: str, max_results: int = 3):
    """
    Real web search provider using Tavily.

    Time Complexity:
    - External API call depends on network latency.
    - Result formatting: O(r * c), where:
      r = number of results
      c = average content length per result.
    """

    if not TAVILY_API_KEY:
        return mock_search(query)

    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=TAVILY_API_KEY)

        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="basic"
        )

        results = response.get("results", [])
        formatted_results = []

        for result in results:
            formatted_results.append(
                {
                    "title": clean_text(result.get("title", "Untitled Source"), 120),
                    "url": result.get("url", ""),
                    "snippet": clean_text(result.get("content", ""), 500)
                }
            )

        return formatted_results or mock_search(query)

    except Exception as error:
        print(f"Tavily search failed: {error}")
        return mock_search(query)


def search_web(query: str):
    """
    Selects the active web search provider.

    Time Complexity:
    - O(1), because provider selection is constant time.
    """

    if SEARCH_PROVIDER == "tavily":
        return tavily_search(query)

    return mock_search(query)