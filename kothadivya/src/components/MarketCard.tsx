import { useEffect, useState } from "react";
import { getStockPrice } from "@/api/market";


const MarketCard = ({ symbol }: { symbol: string }) => {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    getStockPrice(symbol).then(setData);
  }, [symbol]);

  return (
    <div>
      <h3>{symbol}</h3>
      <p>Price: {data?.["Global Quote"]?.["05. price"]}</p>
    </div>
  );
};

export default MarketCard;
