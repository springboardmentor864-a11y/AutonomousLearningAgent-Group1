import { ReactNode } from 'react';
import { cn } from '@/lib/utils';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface StatsCardProps {
  title: string;
  value: string;
  change?: number;
  icon: ReactNode;
  className?: string;
}

const StatsCard = ({ title, value, change, icon, className }: StatsCardProps) => {
  const isPositive = change && change > 0;
  const isNegative = change && change < 0;

  return (
    <div className={cn('stat-card', className)}>
      <div className="flex items-start justify-between mb-4">
        <div className="p-3 rounded-lg bg-accent/10">
          {icon}
        </div>
        {change !== undefined && (
          <div className={cn(
            'flex items-center gap-1 text-sm font-medium px-2 py-1 rounded-full',
            isPositive && 'bg-emerald/10 text-emerald',
            isNegative && 'bg-coral/10 text-coral',
            !isPositive && !isNegative && 'bg-muted text-muted-foreground'
          )}>
            {isPositive ? <TrendingUp className="h-3 w-3" /> : isNegative ? <TrendingDown className="h-3 w-3" /> : null}
            <span>{Math.abs(change)}%</span>
          </div>
        )}
      </div>
      <p className="text-sm text-muted-foreground mb-1">{title}</p>
      <p className="text-2xl font-bold font-serif text-foreground">{value}</p>
    </div>
  );
};

export default StatsCard;
