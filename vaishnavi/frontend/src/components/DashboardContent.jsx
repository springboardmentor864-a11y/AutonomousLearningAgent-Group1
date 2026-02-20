import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Zap, BookOpen, Target, Clock } from 'lucide-react';

export function DashboardContent({ token }) {
    const [stats, setStats] = useState(null);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const res = await fetch('http://localhost:8000/dashboard/stats', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                if (res.ok) {
                    const data = await res.json();
                    setStats(data);
                }
            } catch (err) {
                console.error("Failed to fetch stats", err);
            }
        };
        fetchStats();
    }, [token]);

    if (!stats) return <div>Loading Stats...</div>;

    return (
        <div className="fade-in">
            <h1 style={{ fontSize: '2rem', marginBottom: '2rem', color: '#1f2937' }}>Your Learning Dashboard</h1>

            <div className="stats-grid">
                <div className="stat-card">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <div style={{ background: '#e0e7ff', padding: '10px', borderRadius: '50%' }}>
                            <Zap size={24} color="#4338ca" />
                        </div>
                        <div>
                            <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Average Score</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{stats.average_score.toFixed(1)}%</div>
                        </div>
                    </div>
                </div>

                <div className="stat-card">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <div style={{ background: '#dcfce7', padding: '10px', borderRadius: '50%' }}>
                            <Target size={24} color="#15803d" />
                        </div>
                        <div>
                            <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Best Score</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{stats.best_score.toFixed(1)}%</div>
                        </div>
                    </div>
                </div>

                <div className="stat-card">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <div style={{ background: '#fee2e2', padding: '10px', borderRadius: '50%' }}>
                            <BookOpen size={24} color="#b91c1c" />
                        </div>
                        <div>
                            <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Total Quizzes</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{stats.total_quizzes}</div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="stat-card" style={{ height: '400px' }}>
                <h3 style={{ marginBottom: '1.5rem', color: '#374151' }}>Progress Growth</h3>
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                        data={stats.history}
                        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="attempt" label={{ value: 'Attempt', position: 'insideBottomRight', offset: -5 }} />
                        <YAxis label={{ value: 'Score %', angle: -90, position: 'insideLeft' }} />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="score" stroke="#8884d8" activeDot={{ r: 8 }} name="Score" />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
