import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { TrendingUp, Target, Shield, BarChart3, ArrowRight, Loader2 } from 'lucide-react';

const Index = () => {
  const navigate = useNavigate();
  const { user, loading } = useAuth();

  useEffect(() => {
    if (!loading && user) {
      navigate('/dashboard');
    }
  }, [user, loading, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-accent" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0" style={{ background: 'var(--gradient-hero)' }} />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-accent/20 via-transparent to-transparent" />
        
        {/* Navigation */}
        <nav className="relative z-10 container mx-auto px-6 py-6 flex items-center justify-between">
          <h1 className="text-2xl font-serif font-bold text-primary-foreground">
            Wealth<span className="text-accent">Forge</span>
          </h1>
          <Button 
            onClick={() => navigate('/auth')}
            variant="outline"
            className="border-primary-foreground/20 text-primary-foreground hover:bg-primary-foreground/10"
          >
            Sign In
          </Button>
        </nav>

        {/* Hero Content */}
        <div className="relative z-10 container mx-auto px-6 py-24 lg:py-32">
          <div className="max-w-3xl">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-serif font-bold text-primary-foreground mb-6 leading-tight">
              Shape Your <span className="text-accent">Financial</span> Destiny
            </h1>
            <p className="text-xl text-primary-foreground/80 mb-8 max-w-2xl">
              Personalized wealth management that helps you plan goals, build portfolios, 
              and track your progress towards financial freedom.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Button 
                size="lg"
                onClick={() => navigate('/auth')}
                className="bg-accent hover:bg-accent/90 text-accent-foreground"
              >
                Get Started Free
                <ArrowRight className="h-5 w-5 ml-2" />
              </Button>
              <Button 
                size="lg"
                variant="outline"
                className="border-primary-foreground/20 text-primary-foreground hover:bg-primary-foreground/10"
              >
                Learn More
              </Button>
            </div>
          </div>
        </div>

        {/* Decorative elements */}
        <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-accent/10 rounded-full blur-3xl transform translate-x-1/3 translate-y-1/3" />
      </div>

      {/* Features Section */}
      <section className="py-24 bg-background">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-serif font-bold text-foreground mb-4">
              Everything You Need to Build Wealth
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Comprehensive tools and insights to help you achieve your financial goals
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="p-6 rounded-xl bg-card shadow-lg hover-lift">
              <div className="p-3 rounded-lg bg-accent/10 w-fit mb-4">
                <Target className="h-6 w-6 text-accent" />
              </div>
              <h3 className="text-xl font-serif font-semibold mb-2">Goal Planning</h3>
              <p className="text-muted-foreground">
                Set and track retirement, home, education, and custom financial goals
              </p>
            </div>

            <div className="p-6 rounded-xl bg-card shadow-lg hover-lift">
              <div className="p-3 rounded-lg bg-accent/10 w-fit mb-4">
                <BarChart3 className="h-6 w-6 text-accent" />
              </div>
              <h3 className="text-xl font-serif font-semibold mb-2">Portfolio Builder</h3>
              <p className="text-muted-foreground">
                Build diversified portfolios with stocks, ETFs, and mutual funds
              </p>
            </div>

            <div className="p-6 rounded-xl bg-card shadow-lg hover-lift">
              <div className="p-3 rounded-lg bg-accent/10 w-fit mb-4">
                <TrendingUp className="h-6 w-6 text-accent" />
              </div>
              <h3 className="text-xl font-serif font-semibold mb-2">Live Tracking</h3>
              <p className="text-muted-foreground">
                Real-time dashboards with market-linked updates and performance metrics
              </p>
            </div>

            <div className="p-6 rounded-xl bg-card shadow-lg hover-lift">
              <div className="p-3 rounded-lg bg-accent/10 w-fit mb-4">
                <Shield className="h-6 w-6 text-accent" />
              </div>
              <h3 className="text-xl font-serif font-semibold mb-2">Smart Insights</h3>
              <p className="text-muted-foreground">
                Personalized recommendations based on your financial profile
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-secondary">
        <div className="container mx-auto px-6 text-center">
          <h2 className="text-3xl md:text-4xl font-serif font-bold text-foreground mb-4">
            Start Your Wealth Journey Today
          </h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-xl mx-auto">
            Join thousands of users who are taking control of their financial future with WealthForge.
          </p>
          <Button 
            size="lg"
            onClick={() => navigate('/auth')}
            className="bg-accent hover:bg-accent/90"
          >
            Create Free Account
            <ArrowRight className="h-5 w-5 ml-2" />
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-primary text-primary-foreground">
        <div className="container mx-auto px-6">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <h1 className="text-xl font-serif font-bold mb-4 md:mb-0">
              Wealth<span className="text-accent">Forge</span>
            </h1>
            <p className="text-primary-foreground/60 text-sm">
              © 2024 WealthForge. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
