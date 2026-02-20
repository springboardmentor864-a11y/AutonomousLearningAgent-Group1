import requests
from app.core.config import YAHOO_FINANCE_BASE_URL

def get_stock_price(symbol: str):
    url = f"{YAHOO_FINANCE_BASE_URL}/v8/finance/chart/{symbol}"
    res = requests.get(url)
    res.raise_for_status()

    data = res.json()
    price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]

    return {
        "symbol": symbol,
        "last_price": price
    }
