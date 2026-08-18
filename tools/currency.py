from langchain_core.tools import tool
import requests


@tool
def currency_converter(
    amount: float,
    from_currency: str,
    to_currency: str,
) -> str:
    """
    Converts one currency into another using the latest exchange rate.
    """

    try:

        response = requests.get(
            f"https://open.er-api.com/v6/latest/{from_currency.upper()}",
            timeout=10
        )

        data = response.json()

        if data["result"] != "success":
            return "Unable to fetch exchange rates."

        rate = data["rates"][to_currency.upper()]

        converted = amount * rate

        return (
            f"{amount:.2f} {from_currency.upper()} = "
            f"{converted:.2f} {to_currency.upper()}"
        )

    except Exception as ex:

        return str(ex)