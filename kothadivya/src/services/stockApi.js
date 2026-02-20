export function fetchStockPrice(symbol) {
  return fetch(`http://127.0.0.1:8000/stocks/${symbol}`)
    .then(res => res.json());
}
