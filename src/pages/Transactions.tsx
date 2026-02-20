import { useEffect, useState } from "react";
import {
  getTransactions,
  createTransaction, 

} from "../services/transactionService";

type Transaction = {
  id: number;
  user_id: number;
  type: "income" | "expense";
  amount: number;
  category?: string;
  description?: string;
  created_at: string;
};

const Transactions = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // form state
  const [type, setType] = useState<"income" | "expense">("income");
  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("");
  const [description, setDescription] = useState("");

  const fetchTransactions = () => {
    setLoading(true);
    getTransactions()
      .then((res) => setTransactions(res.data))
      .catch(() => setError("Failed to fetch transactions"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchTransactions();
  }, []);

  const handleAddTransaction = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      await createTransaction({
        type,
        amount: Number(amount),
        category: category || null,
        description: description || null,
});

      // reset form
      setAmount("");
      setCategory("");
      setDescription("");
      setType("income");

      fetchTransactions();
    } catch (err: any) {
      setError("Failed to add transaction");
    }
  };

  if (loading) return <p>Loading...</p>;
  if (error) return <p className="text-red-500">{error}</p>;

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Transactions</h1>

      {/* ➕ Add Transaction Form */}
      <form
        onSubmit={handleAddTransaction}
        className="border p-4 rounded space-y-3"
      >
        <h2 className="font-semibold">Add Transaction</h2>

        <select
          value={type}
          onChange={(e) =>
            setType(e.target.value as "income" | "expense")
          }
          className="border p-2 w-full"
        >
          <option value="income">Income</option>
          <option value="expense">Expense</option>
        </select>

        <input
          type="number"
          step="0.01"
          placeholder="Amount"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          required
          className="border p-2 w-full"
        />

        <input
          type="text"
          placeholder="Category (optional)"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="border p-2 w-full"
        />

        <input
          type="text"
          placeholder="Description (optional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="border p-2 w-full"
        />

        <button
          type="submit"
          className="bg-black text-white px-4 py-2 rounded"
        >
          Add Transaction
        </button>
      </form>

      {/* 📋 Transactions Table */}
      <table className="w-full border">
        <thead>
          <tr className="bg-gray-100">
            <th className="border p-2">Type</th>
            <th className="border p-2">Amount</th>
            <th className="border p-2">Category</th>
            <th className="border p-2">Description</th>
            <th className="border p-2">Date</th>
          </tr>
        </thead>

        <tbody>
          {transactions.map((tx) => (
            <tr key={tx.id}>
              <td className="border p-2 capitalize">{tx.type}</td>
              <td className="border p-2">{tx.amount}</td>
              <td className="border p-2">{tx.category || "-"}</td>
              <td className="border p-2">{tx.description || "-"}</td>
              <td className="border p-2">
                {new Date(tx.created_at).toLocaleDateString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Transactions;
