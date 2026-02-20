import { useEffect, useState } from "react";
import API from "../api";
import "./Goals.css";

/* ---------------- TYPES ---------------- */


interface Goal {
  id: number;
  user_id: number;
  goal_type: string;
  target_amount: number;
  target_date: string;
  monthly_contribution?: number;
  status: string;
  created_at: string;
}

interface GoalForm {
  goal_type: string;
  target_amount: string;
  target_date: string;
  monthly_contribution: string;
}

const Goals = () => {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [userId, setUserId] = useState<number | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);

  const [form, setForm] = useState<GoalForm>({
    goal_type: "custom",
    target_amount: "",
    target_date: "",
    monthly_contribution: "",
  });

  /* -----------------------------------
     FETCH CURRENT USER + GOALS
  ----------------------------------- */
  useEffect(() => {
    API.get("/auth/me")
      .then((res) => {
        setUserId(res.data.id);
        fetchGoals(res.data.id);
      })
      .catch(() => alert("Authentication error"));
  }, []);

  const fetchGoals = (uid: number) => {
    API.get(`/goals/user/${uid}`)
      .then((res) => setGoals(res.data))
      .catch(() => alert("Failed to fetch goals"));
  };

  /* -----------------------------------
     FORM HANDLING
  ----------------------------------- */
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  /* -----------------------------------
     CREATE / UPDATE GOAL
  ----------------------------------- */
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!userId) return;

    const payload = {
      ...form,
      user_id: userId,
    };

    if (editingId) {
      API.put(`/goals/${editingId}`, payload)
        .then(() => {
          fetchGoals(userId);
          resetForm();
        })
        .catch(() => alert("Failed to update goal"));
    } else {
      API.post("/goals/", payload)
        .then(() => {
          fetchGoals(userId);
          resetForm();
        })
        .catch(() => alert("Failed to create goal"));
    }
  };

  const resetForm = () => {
    setEditingId(null);
    setForm({
      goal_type: "custom",
      target_amount: "",
      target_date: "",
      monthly_contribution: "",
    });
  };

  /* -----------------------------------
     EDIT GOAL
  ----------------------------------- */
  const editGoal = (goal: Goal) => {
    setEditingId(goal.id);
    setForm({
      goal_type: goal.goal_type,
      target_amount: String(goal.target_amount),
      target_date: goal.target_date,
      monthly_contribution: goal.monthly_contribution
        ? String(goal.monthly_contribution)
        : "",
    });
  };

  /* -----------------------------------
     DELETE GOAL
  ----------------------------------- */
  const deleteGoal = (id: number) => {
    if (!window.confirm("Delete this goal?")) return;

    API.delete(`/goals/${id}`)
      .then(() => fetchGoals(userId!))
      .catch(() => alert("Delete failed"));
  };

  /* -----------------------------------
     MARK GOAL COMPLETED
  ----------------------------------- */
  const markCompleted = (id: number) => {
    API.put(`/goals/${id}`, { status: "completed" })
      .then(() => fetchGoals(userId!))
      .catch(() => alert("Failed to mark completed"));
  };

  /* -----------------------------------
     PROGRESS CALCULATION (TIME-BASED)
  ----------------------------------- */
  const calculateProgress = (goal: Goal): number => {
    if (
      !goal.monthly_contribution ||
      !goal.target_amount ||
      !goal.created_at
    ) {
      return 0;
    }

    const createdDate = new Date(goal.created_at);
    const today = new Date();

    let monthsPassed =
      (today.getFullYear() - createdDate.getFullYear()) * 12 +
      (today.getMonth() - createdDate.getMonth());

    monthsPassed = Math.max(monthsPassed, 1);

    const invested = goal.monthly_contribution * monthsPassed;

    return Math.min((invested / goal.target_amount) * 100, 100);
  };

  /* -----------------------------------
     UI
  ----------------------------------- */
  return (
    <div className="goals-page">
      <h1>🎯 Financial Goals</h1>

      {/* GOAL FORM */}
      <form className="goal-form" onSubmit={handleSubmit}>
        <select
          name="goal_type"
          value={form.goal_type}
          onChange={handleChange}
        >
          <option value="retirement">Retirement</option>
          <option value="home">Home</option>
          <option value="education">Education</option>
          <option value="custom">Custom</option>
        </select>

        <input
          type="number"
          name="target_amount"
          placeholder="Target Amount"
          value={form.target_amount}
          onChange={handleChange}
          required
        />

        <input
          type="date"
          name="target_date"
          value={form.target_date}
          onChange={handleChange}
          required
        />

        <input
          type="number"
          name="monthly_contribution"
          placeholder="Monthly Contribution"
          value={form.monthly_contribution}
          onChange={handleChange}
        />

        <button type="submit">
          {editingId ? "Update Goal" : "Add Goal"}
        </button>
      </form>

      {/* GOALS LIST */}
      <div className="goals-list">
        {goals.length === 0 && <p>No goals found.</p>}

        {goals.map((goal) => {
          const progress = calculateProgress(goal);

          return (
            <div key={goal.id} className="goal-card">
              <h3>{goal.goal_type.toUpperCase()}</h3>

              <p>Target: ₹{goal.target_amount}</p>
              <p>Target Date: {goal.target_date}</p>
              <p>
                Status: <strong>{goal.status}</strong>
              </p>

              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${progress}%` }}
                />
              </div>

              <span className="progress-text">
                {progress.toFixed(1)}% progress (time-based)
              </span>

              <div className="goal-actions">
                <button onClick={() => editGoal(goal)}>Edit</button>
                <button onClick={() => deleteGoal(goal.id)}>Delete</button>

                {goal.status !== "completed" && (
                  <button onClick={() => markCompleted(goal.id)}>
                    Mark Completed
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Goals;
