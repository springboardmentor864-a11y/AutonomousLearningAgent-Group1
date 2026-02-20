import { useEffect, useState } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Lightbulb, AlertCircle, TrendingUp, Shield, Check } from 'lucide-react';
import { cn } from '@/lib/utils';
import { format } from 'date-fns';

interface Recommendation {
  id: string;
  title: string;
  description: string;
  type: string;
  priority: string;
  is_read: boolean;
  created_at: string;
}

const typeIcons: Record<string, React.ReactNode> = {
  investment: <TrendingUp className="h-5 w-5" />,
  risk: <Shield className="h-5 w-5" />,
  alert: <AlertCircle className="h-5 w-5" />,
  tip: <Lightbulb className="h-5 w-5" />,
};

const priorityColors: Record<string, string> = {
  high: 'bg-coral/10 text-coral border-coral/20',
  medium: 'bg-gold/10 text-gold border-gold/20',
  low: 'bg-emerald/10 text-emerald border-emerald/20',
};

const Recommendations = () => {
  const { user } = useAuth();
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      fetchRecommendations();
    }
  }, [user]);

  const fetchRecommendations = async () => {
    const { data, error } = await supabase
      .from('recommendations')
      .select('*')
      .eq('user_id', user?.id)
      .order('created_at', { ascending: false });

    if (!error && data) {
      setRecommendations(data);
    }
    setLoading(false);
  };

  const markAsRead = async (id: string) => {
    await supabase
      .from('recommendations')
      .update({ is_read: true })
      .eq('id', id);
    
    setRecommendations(recommendations.map((r) => 
      r.id === id ? { ...r, is_read: true } : r
    ));
  };

  const unreadCount = recommendations.filter((r) => !r.is_read).length;

  if (loading) {
    return (
      <div className="space-y-8 animate-pulse">
        <div className="h-8 bg-muted rounded w-1/3" />
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 bg-muted rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-serif font-bold text-foreground mb-2">Recommendations</h1>
          <p className="text-muted-foreground">Personalized insights for your financial journey</p>
        </div>
        {unreadCount > 0 && (
          <span className="px-3 py-1 text-sm font-medium rounded-full bg-accent text-accent-foreground">
            {unreadCount} unread
          </span>
        )}
      </div>

      {recommendations.length === 0 ? (
        <Card className="border-0 shadow-lg">
          <CardContent className="py-12 text-center">
            <Lightbulb className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-xl font-serif font-semibold mb-2">No recommendations yet</h3>
            <p className="text-muted-foreground">
              As you use the platform, we'll provide personalized insights based on your financial activity.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {recommendations.map((rec) => {
            const icon = typeIcons[rec.type.toLowerCase()] || typeIcons.tip;
            const priorityClass = priorityColors[rec.priority.toLowerCase()] || priorityColors.low;

            return (
              <Card 
                key={rec.id} 
                className={cn(
                  'border-0 shadow-lg cursor-pointer transition-all',
                  !rec.is_read && 'ring-2 ring-accent/20'
                )}
                onClick={() => !rec.is_read && markAsRead(rec.id)}
              >
                <CardContent className="pt-6">
                  <div className="flex items-start gap-4">
                    <div className={cn('p-3 rounded-lg border', priorityClass)}>
                      {icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-semibold text-lg">{rec.title}</h3>
                        <span className={cn(
                          'px-2 py-0.5 text-xs rounded-full capitalize',
                          priorityClass
                        )}>
                          {rec.priority}
                        </span>
                        {rec.is_read && (
                          <span className="flex items-center gap-1 text-xs text-muted-foreground">
                            <Check className="h-3 w-3" />
                            Read
                          </span>
                        )}
                      </div>
                      <p className="text-muted-foreground mb-3">{rec.description}</p>
                      <p className="text-sm text-muted-foreground">
                        {format(new Date(rec.created_at), 'MMMM d, yyyy')}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Recommendations;
