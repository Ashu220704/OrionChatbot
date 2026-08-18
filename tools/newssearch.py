from langchain_core.tools import tool
from ddgs import DDGS


@tool
def latest_news(topic: str) -> str:
    """
    Search for the latest news on any topic.
    """

    try:

        with DDGS() as ddgs:

            results = list(
                ddgs.news(
                    query=topic,
                    max_results=5
                )
)

        if not results:
            return "No news found."

        output = []

        for index, article in enumerate(results, start=1):

            output.append(
                f"{index}. {article['title']}\n"
                f"{article['date']}\n"
                f"{article['url']}\n"
            )

        return "\n".join(output)

    except Exception as ex:

        return str(ex)