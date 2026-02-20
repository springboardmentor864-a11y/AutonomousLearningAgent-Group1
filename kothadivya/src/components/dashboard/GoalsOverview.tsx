import { Target } from "lucide-react";

interface Goal {
  id: number;
  goal_type: string;
  target_amount: number;
  monthly_contribution?: number;
  created_at: string;
  status: string;
}

interface Props {
  goals: Goal[];
  loading: boolean;
}

const GoalsOverview = ({ goals, loading }: Props) => {
  const calculateProgress = (goal: Goal) => {
    if (!goal.monthly_contribution || !goal.target_amount) return 0;

    const created = new Date(goal.created_at);
    const today = new Date();

    let months =
      (today.getFullYear() - created.getFullYear()) * 12 +
      (today.getMonth() - created.getMonth());

    months = Math.max(months, 1);

    const invested = goal.monthly_contribution * months;
    return Math.min((invested / goal.target_amount) * 100, 100);
  };

  if (loading) {
    return (
      <div className="p-6 border rounded-xl text-muted-foreground">
        Loading goals...
      </div>
    );
  }

  if (goals.length === 0) {
    return (
      <div className="p-6 border rounded-xl text-muted-foreground">
        No goals yet. Create your first goal 🎯
      </div>
    );
  }

  return (
    <div className="p-6 border rounded-xl space-y-4">
      <div className="flex items-center gap-2">
        <Target className="h-5 w-5 text-accent" />
        <h2 className="font-semibold">Goals Overview</h2>
      </div>

      {goals.slice(0, 3).map((goal) => {
        const progress = calculateProgress(goal);

        return (
          <div key={goal.id} className="space-y-1">
            <div className="flex justify-between text-sm">
              <span className="capitalize">
                {goal.goal_type}
              </span>
              <span>{progress.toFixed(1)}%</span>
            </div>

            <div className="h-2 bg-muted rounded">
              <div
                className="h-2 bg-accent rounded"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default GoalsOverview;
