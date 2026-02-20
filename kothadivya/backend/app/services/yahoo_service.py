import yfinance as yf
from decimal import Decimal

def get_stock_summary(symbol: str):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info

        if not info:
            return None

        # Safely extract prices
        current_price = (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
        )

        last_price = info.get("previousClose")

        if current_price is None:
            return None

        return {
            "symbol": symbol,
            "company_name": info.get("shortName", ""),
            "currency": info.get("currency", "USD"),

            # ✅ Prices you asked for
            "current_value": Decimal(str(current_price)),
            "last_price": Decimal(str(last_price)) if last_price else None,

            # Optional extras
            "day_high": info.get("dayHigh"),
            "day_low": info.get("dayLow"),
            "market_cap": info.get("marketCap"),
        }

    except Exception as e:
        print("Yahoo Finance error:", e)
        return None
