import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

/* ---------- TYPES ---------- */
export interface Transaction {
  id: number;
  type: "income" | "expense";
  amount: number;
  created_at: string;
}

interface TransactionsOverviewProps {
  transactions: Transaction[];
  loading: boolean;
}

/* ---------- COMPONENT ---------- */
const TransactionsOverview = ({
  transactions,
  loading,
}: TransactionsOverviewProps) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Transactions</CardTitle>
      </CardHeader>

      <CardContent>
        {loading ? (
          <p className="text-muted-foreground">
            Loading transactions...
          </p>
        ) : transactions.length === 0 ? (
          <p className="text-muted-foreground">
            No transactions yet
          </p>
        ) : (
          <ul className="space-y-3">
            {transactions.map((tx) => (
              <li
                key={tx.id}
                className="flex justify-between border-b pb-2"
              >
                <span className="capitalize">{tx.type}</span>
                <span
                  className={
                    tx.type === "income"
                      ? "text-green-600"
                      : "text-red-600"
                  }
                >
                  ₹{tx.amount}
                </span>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
};

export default TransactionsOverview;
