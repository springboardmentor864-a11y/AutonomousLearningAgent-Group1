export const addTransaction = async (
  amount,
  category,
  transactionType,
  description,
  token
) => {

  // 🔴 ADD THIS LINE
  console.log("TOKEN:", token);

  const response = await fetch("http://127.0.0.1:8000/transactions/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      amount: Number(amount),
      category,
      transaction_type: transactionType,
      description,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    console.error("Backend error:", error);
    throw new Error(error.detail || "Failed to add transaction");
  }

  return await response.json();
};
