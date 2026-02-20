import { useEffect, useState } from "react";
import API from "@/api";
import { getStockPrice } from "@/api/market";

import StatsCard from "@/components/dashboard/StatsCard";
import GoalsOverview from "@/components/dashboard/GoalsOverview";
import InvestmentsOverview from "@/components/dashboard/InvestmentsOverview";
import TransactionsOverview from "@/components/dashboard/TransactionsOverview";
import RecommendationsOverview from "@/components/dashboard/RecommendationsOverview";

import {
  Wallet,
  TrendingUp,
  Target,
  PiggyBank,
  FileText,
} from "lucide-react";

/* ---------------- TYPES ---------------- */

interface Goal {
  id: number;
  goal_type: string;
  target_amount: number;
  monthly_contribution?: number;
  created_at: string;
  status: string;
}

interface Investment {
  id: number;
  amount: number;
  type: string;
  created_at: string;
}

interface Transaction {
  id: number;
  type: "income" | "expense";
  amount: number;
  created_at: string;
}

/* ---------------- COMPONENT ---------------- */

const Dashboard = () => {
  const [userName, setUserName] = useState("there");

  const [goals, setGoals] = useState<Goal[]>([]);
  const [investments, setInvestments] = useState<Investment[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);

  const [loadingGoals, setLoadingGoals] = useState(true);
  const [loadingInvestments, setLoadingInvestments] = useState(true);
  const [loadingTransactions, setLoadingTransactions] = useState(true);

  /* Alpha Vantage */
  const [stockPrice, setStockPrice] = useState<number | null>(null);
  const [loadingStock, setLoadingStock] = useState(true);

  /* ---------------- REPORT DOWNLOAD ---------------- */

  const downloadReport = () => {
    window.open(
      "http://localhost:8000/reports/wealth/pdf",
      "_blank"
    );
  };

  /* ---------------- FETCH USER + DATA ---------------- */

  useEffect(() => {
    API.get("/auth/me")
      .then((res) => {
        const userId = res.data.id;
        setUserName(res.data.full_name?.split(" ")[0] || "there");

        return Promise.all([
          API.get(`/goals/user/${userId}`),
          API.get(`/investments/user/${userId}`),
          API.get(`/transactions/user/${userId}`),
        ]);
      })
      .then(([goalsRes, investmentsRes, transactionsRes]) => {
        setGoals(goalsRes.data || []);
        setInvestments(investmentsRes.data || []);
        setTransactions(transactionsRes.data || []);
      })
      .catch((err) => {
        console.error("Dashboard fetch error:", err);
        setGoals([]);
        setInvestments([]);
        setTransactions([]);
      })
      .finally(() => {
        setLoadingGoals(false);
        setLoadingInvestments(false);
        setLoadingTransactions(false);
      });
  }, []);

  /* ---------------- FETCH STOCK ---------------- */

  useEffect(() => {
    getStockPrice("AAPL")
      .then((data) => {
        setStockPrice(data.price);
      })
      .catch((err) => {
        console.error("Stock API error:", err);
      })
      .finally(() => setLoadingStock(false));
  }, []);

  /* ---------------- GREETING ---------------- */

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning";
    if (hour < 18) return "Good afternoon";
    return "Good evening";
  };

  /* ---------------- GOALS PROGRESS ---------------- */

  const calculateOverallGoalsProgress = () => {
    if (goals.length === 0) return 0;

    let total = 0;
    let count = 0;

    goals.forEach((goal) => {
      if (!goal.monthly_contribution) return;

      const created = new Date(goal.created_at);
      const today = new Date();

      let months =
        (today.getFullYear() - created.getFullYear()) * 12 +
        (today.getMonth() - created.getMonth());

      months = Math.max(months, 1);

      total +=
        ((goal.monthly_contribution * months) /
          goal.target_amount) *
        100;

      count++;
    });

    return count ? Math.min(total / count, 100) : 0;
  };

  const goalsProgress = calculateOverallGoalsProgress();

  /* ---------------- STATS ---------------- */

  const totalInvestments = investments.reduce(
    (sum, inv) => sum + inv.amount,
    0
  );

  const totalSavings = transactions.reduce((sum, tx) => {
    return tx.type === "income"
      ? sum + tx.amount
      : sum - tx.amount;
  }, 0);

  /* ---------------- UI ---------------- */

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-serif font-bold">
          {getGreeting()}, {userName}
        </h1>
        <p className="text-muted-foreground">
          Here's an overview of your financial journey
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <StatsCard
          title="Total Portfolio"
          value={
            loadingInvestments
              ? "—"
              : investments.length === 0
              ? "No Investments"
              : `₹${totalInvestments}`
          }
          change={0}
          icon={<Wallet className="h-6 w-6 text-accent" />}
        />

        <StatsCard
          title="Live Stock (AAPL)"
          value={
            loadingStock
              ? "—"
              : stockPrice
              ? `₹${stockPrice}`
              : "N/A"
          }
          change={0}
          icon={<TrendingUp className="h-6 w-6 text-accent" />}
        />

        <StatsCard
          title="Goals Progress"
          value={
            loadingGoals ? "—" : `${goalsProgress.toFixed(1)}%`
          }
          change={0}
          icon={<Target className="h-6 w-6 text-accent" />}
        />

        <StatsCard
          title="Total Savings"
          value={
            loadingTransactions ? "—" : `₹${totalSavings}`
          }
          change={0}
          icon={<PiggyBank className="h-6 w-6 text-accent" />}
        />

       <div
  onClick={downloadReport}
  className="cursor-pointer hover:opacity-90"
>
  <StatsCard
    title="Wealth Report"
    value="Download PDF"
    change={0}
    icon={<FileText className="h-6 w-6 text-accent" />}
  />
</div>

      </div>

      {/* Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <GoalsOverview goals={goals} loading={loadingGoals} />
        <InvestmentsOverview
          investments={investments}
          loading={loadingInvestments}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TransactionsOverview
          transactions={transactions}
          loading={loadingTransactions}
        />
        <RecommendationsOverview />
      </div>
    </div>
  );
};

export default Dashboard;
