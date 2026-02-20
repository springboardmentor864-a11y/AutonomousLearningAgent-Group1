import { useEffect, useState } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { Briefcase, TrendingUp, TrendingDown, BarChart3 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Investment {
  id: string;
  user_id: string;
  name: string;
  symbol: string | null;
  type: string;
  quantity: number;
  purchase_price: number;
  current_price: number | null;
  created_at: string;
}

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

const Portfolio = () => {
  const { user } = useAuth();

  const [investments, setInvestments] = useState<Investment[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingInvestment, setEditingInvestment] = useState<Investment | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (user?.id) fetchInvestments();
  }, [user]);

  /* ================= FETCH ================= */

  const fetchInvestments = async () => {
    setLoading(true);

    const { data, error } = await supabase
      .from('investments')
      .select('*')
      .eq('user_id', String(user!.id)) // ✅ FIX
      .order('created_at', { ascending: false });

    if (!error && data) setInvestments(data);
    setLoading(false);
  };

  /* ================= UPDATE ================= */

  const updateInvestment = async () => {
    if (!editingInvestment || !user?.id) return;

    setSaving(true);

    const { error } = await supabase
      .from('investments')
      .update({
        name: editingInvestment.name,
        symbol: editingInvestment.symbol,
        type: editingInvestment.type,
        quantity: editingInvestment.quantity,
        purchase_price: editingInvestment.purchase_price,
        current_price: editingInvestment.current_price,
      })
      .eq('id', editingInvestment.id)
      .eq('user_id', String(user.id)); // ✅ FIX

    setSaving(false);

    if (!error) {
      setEditingInvestment(null);
      fetchInvestments();
    } else {
      console.error('Update error:', error);
    }
  };

  /* ================= HELPERS ================= */

  const formatCurrency = (amount: number) =>
    new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);

  const totalValue = investments.reduce((acc, inv) => {
    const price = inv.current_price ?? inv.purchase_price;
    return acc + inv.quantity * price;
  }, 0);

  const totalGain = investments.reduce((acc, inv) => {
    const price = inv.current_price ?? inv.purchase_price;
    return acc + (price - inv.purchase_price) * inv.quantity;
  }, 0);

  const gainPercentage =
    totalValue > 0 ? (totalGain / (totalValue - totalGain)) * 100 : 0;

  const allocationData = () => {
    const map: Record<string, number> = {};
    investments.forEach((inv) => {
      const value = inv.quantity * (inv.current_price ?? inv.purchase_price);
      map[inv.type] = (map[inv.type] || 0) + value;
    });
    return Object.entries(map).map(([name, value]) => ({ name, value }));
  };

  if (loading) {
    return <div className="h-40 animate-pulse bg-muted rounded-xl" />;
  }

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-serif font-bold">Portfolio</h1>

      {/* SUMMARY */}
      <div className="grid md:grid-cols-3 gap-6">
        <SummaryCard title="Total Value" value={formatCurrency(totalValue)} icon={<Briefcase />} />
        <SummaryCard
          title="Total Gain/Loss"
          value={`${totalGain >= 0 ? '+' : ''}${formatCurrency(totalGain)}`}
          icon={totalGain >= 0 ? <TrendingUp /> : <TrendingDown />}
          positive={totalGain >= 0}
        />
        <SummaryCard
          title="Return Rate"
          value={`${gainPercentage >= 0 ? '+' : ''}${gainPercentage.toFixed(2)}%`}
          icon={<BarChart3 />}
          positive={gainPercentage >= 0}
        />
      </div>

      {/* CHART + HOLDINGS */}
      <div className="grid lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Asset Allocation</CardTitle>
          </CardHeader>
          <CardContent>
            {investments.length === 0 ? (
              <p className="text-muted-foreground text-center">No investments</p>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie data={allocationData()} dataKey="value" innerRadius={60} outerRadius={100}>
                    {allocationData().map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(v: number) => formatCurrency(v)} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Holdings</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 max-h-[300px] overflow-y-auto">
            {investments.map((inv) => {
              const price = inv.current_price ?? inv.purchase_price;
              return (
                <div key={inv.id} className="flex justify-between p-3 bg-secondary rounded-lg">
                  <div>
                    <p className="font-semibold">{inv.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {inv.quantity} × {formatCurrency(price)}
                    </p>
                  </div>
                  <button
                    onClick={() => setEditingInvestment(inv)}
                    className="text-primary text-sm hover:underline"
                  >
                    Edit
                  </button>
                </div>
              );
            })}
          </CardContent>
        </Card>
      </div>

      {/* EDIT MODAL */}
      {editingInvestment && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background p-6 rounded-xl w-full max-w-md space-y-3">
            <h2 className="text-xl font-bold">Edit Investment</h2>

            {['name', 'symbol', 'type'].map((field) => (
              <input
                key={field}
                className="w-full border p-2 rounded"
                value={(editingInvestment as any)[field] ?? ''}
                onChange={(e) =>
                  setEditingInvestment({
                    ...editingInvestment,
                    [field]: e.target.value,
                  })
                }
                placeholder={field}
              />
            ))}

            {['quantity', 'purchase_price', 'current_price'].map((field) => (
              <input
                key={field}
                type="number"
                className="w-full border p-2 rounded"
                value={(editingInvestment as any)[field] ?? 0}
                onChange={(e) =>
                  setEditingInvestment({
                    ...editingInvestment,
                    [field]: Number(e.target.value),
                  })
                }
                placeholder={field}
              />
            ))}

            <div className="flex justify-end gap-3 pt-3">
              <button onClick={() => setEditingInvestment(null)}>Cancel</button>
              <button
                onClick={updateInvestment}
                disabled={saving}
                className="bg-primary text-primary-foreground px-4 py-2 rounded"
              >
                {saving ? 'Saving...' : 'Update'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

/* SUMMARY CARD */
const SummaryCard = ({
  title,
  value,
  icon,
  positive = true,
}: {
  title: string;
  value: string;
  icon: React.ReactNode;
  positive?: boolean;
}) => (
  <Card>
    <CardContent className="pt-6 flex gap-4 items-center">
      <div className={cn('p-3 rounded-lg', positive ? 'bg-emerald/10' : 'bg-coral/10')}>
        {icon}
      </div>
      <div>
        <p className="text-sm text-muted-foreground">{title}</p>
        <p className={cn('text-xl font-bold', positive ? 'text-emerald' : 'text-coral')}>
          {value}
        </p>
      </div>
    </CardContent>
  </Card>
);

export default Portfolio;
