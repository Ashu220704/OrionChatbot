from langchain_core.tools import tool
from ddgs import DDGS


@tool
def internet_search(query: str) -> str:
    """
    Search the internet using DuckDuckGo.

    Use this tool whenever the user asks about:
    - People
    - Companies
    - Technologies
    - General information
    - Latest updates
    """

    try:

        with DDGS() as ddgs:

            results = list(
                ddgs.text(
                    keywords=query,
                    max_results=5
                )
            )

        if not results:
            return "No search results found."

        output = []

        for index, result in enumerate(results, start=1):

            output.append(
                f"{index}. {result['title']}\n"
                f"{result['body']}\n"
                f"{result['href']}\n"
            )

        return "\n".join(output)

    except Exception as ex:

        return str(ex)