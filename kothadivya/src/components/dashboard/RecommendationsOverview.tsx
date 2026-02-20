import { useEffect, useState } from 'react';
import API from '@/api';
import { useAuth } from '@/contexts/AuthContext';
import { Lightbulb, AlertCircle, TrendingUp, Shield } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Recommendation {
  id: string;
  title: string;
  description: string;
  type: string;
  priority: string;
  is_read: boolean;
}

const typeIcons: Record<string, React.ReactNode> = {
  investment: <TrendingUp className="h-5 w-5" />,
  risk: <Shield className="h-5 w-5" />,
  alert: <AlertCircle className="h-5 w-5" />,
  default: <Lightbulb className="h-5 w-5" />,
};

const priorityColors: Record<string, string> = {
  high: 'bg-coral/10 text-coral border-coral/20',
  medium: 'bg-gold/10 text-gold border-gold/20',
  low: 'bg-emerald/10 text-emerald border-emerald/20',
};

const RecommendationsOverview = () => {
  const { user } = useAuth();
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      fetchRecommendations();
    }
  }, [user]);

  const fetchRecommendations = async () => {
    setLoading(true);
    const token = localStorage.getItem('token');
    if (!token) {
      setRecommendations([]);
      setLoading(false);
      return;
    }

    try {
      const res = await API.get('/recommendations?unread=true');
      const data = res.data || [];
      setRecommendations(data.slice(0, 3));
    } catch (err: any) {
      console.error('Failed to fetch recommendations', err);
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (id: string) => {
    try {
      await API.put(`/recommendations/${id}`, { is_read: true });
      setRecommendations(recommendations.filter((r) => r.id !== id));
    } catch (err: any) {
      console.error('Failed to mark recommendation read', err);
    }
  }; 

  if (loading) {
    return (
      <div className="glass-card rounded-xl p-6 animate-pulse">
        <div className="h-6 bg-muted rounded w-1/3 mb-4" />
        <div className="space-y-3">
          {[1, 2].map((i) => (
            <div key={i} className="h-20 bg-muted rounded" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-serif font-semibold">Recommendations</h2>
        {recommendations.length > 0 && (
          <span className="px-2 py-1 text-xs font-medium rounded-full bg-accent text-accent-foreground">
            {recommendations.length} new
          </span>
        )}
      </div>

      {recommendations.length === 0 ? (
        <div className="text-center py-8">
          <Lightbulb className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
          <p className="text-muted-foreground">No new recommendations. You're all caught up!</p>
        </div>
      ) : (
        <div className="space-y-3">
          {recommendations.map((rec) => {
            const icon = typeIcons[rec.type.toLowerCase()] || typeIcons.default;
            const priorityClass = priorityColors[rec.priority.toLowerCase()] || priorityColors.low;

            return (
              <div 
                key={rec.id} 
                className="p-4 rounded-lg bg-secondary/50 hover-lift cursor-pointer"
                onClick={() => markAsRead(rec.id)}
              >
                <div className="flex items-start gap-3">
                  <div className={cn('p-2 rounded-lg border', priorityClass)}>
                    {icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="font-medium">{rec.title}</p>
                      <span className={cn(
                        'px-2 py-0.5 text-xs rounded-full capitalize',
                        priorityClass
                      )}>
                        {rec.priority}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground line-clamp-2">{rec.description}</p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default RecommendationsOverview;
