export async function createInvestment({ token, data }) {
  const response = await fetch("http://127.0.0.1:8000/investments", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || "Failed to create investment");
  }

  return response.json();
}

/* 🔽 CALLING THE FUNCTION 🔽 */

createInvestment({
  token: localStorage.getItem("access_token"),
  data: {
    asset_type: "stock",
    symbol: "AAPL",
    units: 5,
    avg_buy_price: 180,
  },
})
  .then((res) => {
    console.log("✅ Investment created:", res);
  })
  .catch((err) => {
    console.error("❌ Error:", err.message);
  });
