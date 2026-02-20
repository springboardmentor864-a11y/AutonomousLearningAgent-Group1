import { useEffect, useState } from "react";
import API from "@/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";

interface Investment {
  id: number;
  user_id: number;
  asset_type: string;
  symbol: string;
  units: number;
  avg_buy_price: number;
  cost_basis: number;
  current_value: number;
  last_price: number;
  last_price_at: string | null;
}

const Investments = () => {
  // 🔹 TEMP USER ID (replace with auth later)
  const userId = 1;

  const [investments, setInvestments] = useState<Investment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 🔹 New Investment Form State
  const [newInvestment, setNewInvestment] = useState({
    user_id: userId,
    asset_type: "",
    symbol: "",
    units: 0,
    avg_buy_price: 0,
  });

  useEffect(() => {
    fetchInvestments();
  }, []);

  // 🔹 Fetch user investments
  const fetchInvestments = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await API.get(`/investments/user/${userId}`);
      setInvestments(res.data || []);
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Failed to fetch investments"
      );
    } finally {
      setLoading(false);
    }
  };

  // 🔹 Handle form input
  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const { name, value } = e.target;
    setNewInvestment((prev) => ({
      ...prev,
      [name]:
        name === "units" || name === "avg_buy_price"
          ? Number(value)
          : value,
    }));
  };

  // 🔹 Add investment
  const handleAddInvestment = async () => {
    try {
      const res = await API.post("/investments", newInvestment);
      setInvestments((prev) => [...prev, res.data]);

      // Reset form
      setNewInvestment({
        user_id: userId,
        asset_type: "",
        symbol: "",
        units: 0,
        avg_buy_price: 0,
      });
    } catch (err: any) {
      alert(
        err.response?.data?.detail ||
          err.message ||
          "Failed to add investment"
      );
    }
  };

  if (loading) return <p>Loading investments...</p>;
  if (error) return <p className="text-red-500">{error}</p>;

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Investments</h1>

      {/* ➕ Add Investment */}
      <Card className="mb-6 p-4">
        <CardHeader>
          <CardTitle>Add New Investment</CardTitle>
        </CardHeader>

        <CardContent className="grid grid-cols-2 gap-4">
          <div>
            <Label>Asset Type</Label>
            <Input
              name="asset_type"
              value={newInvestment.asset_type}
              onChange={handleInputChange}
              placeholder="stock / crypto"
            />
          </div>

          <div>
            <Label>Symbol</Label>
            <Input
              name="symbol"
              value={newInvestment.symbol}
              onChange={handleInputChange}
              placeholder="AAPL"
            />
          </div>

          <div>
            <Label>Units</Label>
            <Input
              name="units"
              type="number"
              value={newInvestment.units}
              onChange={handleInputChange}
            />
          </div>

          <div>
            <Label>Average Buy Price</Label>
            <Input
              name="avg_buy_price"
              type="number"
              value={newInvestment.avg_buy_price}
              onChange={handleInputChange}
            />
          </div>
        </CardContent>

        <div className="p-4">
          <Button onClick={handleAddInvestment}>
            Add Investment
          </Button>
        </div>
      </Card>

      {/* 📋 Investments List */}
      <div className="grid gap-4">
        {investments.length === 0 && (
          <p className="text-gray-500">No investments yet</p>
        )}

        {investments.map((inv) => (
          <Card key={inv.id}>
            <CardHeader>
              <CardTitle>{inv.symbol}</CardTitle>
            </CardHeader>

            <CardContent>
              <p><strong>Type:</strong> {inv.asset_type}</p>
              <p><strong>Units:</strong> {inv.units}</p>
              <p><strong>Avg Buy Price:</strong> {inv.avg_buy_price}</p>
             
              <p><strong>Current Value:</strong> {inv.current_value}</p>
              <p>
                <strong>Last Price:</strong> {inv.last_price}{" "}
                {inv.last_price_at &&
                  `(as of ${new Date(inv.last_price_at).toLocaleString()})`}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default Investments;
