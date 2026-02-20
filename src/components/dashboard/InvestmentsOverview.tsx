import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

/* ---------- TYPES ---------- */
export interface Investment {
  id: number;
  amount: number;
  type: string;
  created_at: string;
}

interface InvestmentsOverviewProps {
  investments: Investment[];
  loading: boolean;
}

/* ---------- COMPONENT ---------- */
const InvestmentsOverview = ({
  investments,
  loading,
}: InvestmentsOverviewProps) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Investments</CardTitle>
      </CardHeader>

      <CardContent>
        {loading ? (
          <p className="text-muted-foreground">Loading investments...</p>
        ) : investments.length === 0 ? (
          <p className="text-muted-foreground">
            No investments added yet
          </p>
        ) : (
          <ul className="space-y-3">
            {investments.map((inv) => (
              <li
                key={inv.id}
                className="flex justify-between border-b pb-2"
              >
                <span className="capitalize">{inv.type}</span>
                <span className="font-semibold">₹{inv.amount}</span>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
};

export default InvestmentsOverview;
