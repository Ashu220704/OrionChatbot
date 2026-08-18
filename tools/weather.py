from langchain_core.tools import tool
import requests


@tool
def weather(city: str) -> str:
    """
    Returns current weather information for a city.
    """

    try:

        response = requests.get(
            f"https://wttr.in/{city}?format=j1",
            timeout=10
        )

        data = response.json()

        current = data["current_condition"][0]

        return f"""
City : {city}

Temperature : {current['temp_C']} °C

Feels Like : {current['FeelsLikeC']} °C

Humidity : {current['humidity']} %

Condition : {current['weatherDesc'][0]['value']}

Wind Speed : {current['windspeedKmph']} km/h
"""

    except Exception as ex:

        return str(ex)