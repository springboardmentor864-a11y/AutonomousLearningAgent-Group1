import { useState } from "react";

const AddTransaction = () => {
  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("");
  const [transactionType, setTransactionType] = useState("expense");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    // ✅ GET TOKEN
    const token = localStorage.getItem("token");

    console.log("TOKEN SENT:", token);

    if (!token) {
      alert("Login required");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/transactions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          amount: parseFloat(amount),
          category: category.trim(),
          transaction_type: transactionType,
          description: description.trim(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        console.error("Backend error:", data);
        alert(data.detail || "Transaction failed");
        setLoading(false);
        return;
      }

      console.log("Transaction added:", data);
      alert("Transaction added successfully!");

      // ✅ Reset form
      setAmount("");
      setCategory("");
      setDescription("");
      setTransactionType("expense");

    } catch (err) {
      console.error("Network error:", err);
      alert("Server not reachable");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <input
        type="number"
        placeholder="Amount"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        required
      />

      <input
        type="text"
        placeholder="Category"
        value={category}
        onChange={(e) => setCategory(e.target.value)}
        required
      />

      <select
        value={transactionType}
        onChange={(e) => setTransactionType(e.target.value)}
      >
        <option value="expense">Expense</option>
        <option value="income">Income</option>
      </select>

      <input
        type="text"
        placeholder="Description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />

      <button type="submit" disabled={loading}>
        {loading ? "Adding..." : "Add Transaction"}
      </button>
    </form>
  );
};

export default AddTransaction;
