import { useEffect, useState } from "react";
import { fetchStockPrice } from "../services/stockApi";

export default function InvestmentCard() {
  const [lastPrice, setLastPrice] = useState(null);

  useEffect(() => {
    fetchStockPrice("AAPL").then(data => {
      setLastPrice(data.last_price);
    });
  }, []);

  return (
    <div>
      <h2>AAPL</h2>
      <p><b>Last Price:</b> {lastPrice ?? "--"}</p>
    </div>
  );
}
