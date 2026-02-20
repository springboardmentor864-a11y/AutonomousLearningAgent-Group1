import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Calculator, TrendingUp, Home, PiggyBank } from 'lucide-react';

const Calculators = () => {
  // SIP Calculator State
  const [sipMonthly, setSipMonthly] = useState('5000');
  const [sipRate, setSipRate] = useState('12');
  const [sipYears, setSipYears] = useState('10');
  const [sipResult, setSipResult] = useState<{ invested: number; returns: number; total: number } | null>(null);

  // Retirement Calculator State
  const [retireAge, setRetireAge] = useState('60');
  const [currentAge, setCurrentAge] = useState('30');
  const [monthlyExpense, setMonthlyExpense] = useState('50000');
  const [inflationRate, setInflationRate] = useState('6');
  const [retireResult, setRetireResult] = useState<{ corpus: number; monthlySaving: number } | null>(null);

  // Loan EMI Calculator State
  const [loanAmount, setLoanAmount] = useState('1000000');
  const [loanRate, setLoanRate] = useState('8');
  const [loanTenure, setLoanTenure] = useState('20');
  const [loanResult, setLoanResult] = useState<{ emi: number; totalInterest: number; totalAmount: number } | null>(null);

  const calculateSIP = () => {
    const P = parseFloat(sipMonthly);
    const r = parseFloat(sipRate) / 100 / 12;
    const n = parseFloat(sipYears) * 12;
    
    const futureValue = P * ((Math.pow(1 + r, n) - 1) / r) * (1 + r);
    const invested = P * n;
    
    setSipResult({
      invested,
      returns: futureValue - invested,
      total: futureValue,
    });
  };

  const calculateRetirement = () => {
    const yearsToRetire = parseFloat(retireAge) - parseFloat(currentAge);
    const monthlyExp = parseFloat(monthlyExpense);
    const inflation = parseFloat(inflationRate) / 100;
    
    // Future monthly expense considering inflation
    const futureMonthlyExpense = monthlyExp * Math.pow(1 + inflation, yearsToRetire);
    
    // Corpus needed (assuming 25 years post-retirement with 4% withdrawal rate)
    const corpusNeeded = futureMonthlyExpense * 12 * 25;
    
    // Monthly savings needed (assuming 12% returns)
    const r = 0.12 / 12;
    const n = yearsToRetire * 12;
    const monthlySaving = corpusNeeded / (((Math.pow(1 + r, n) - 1) / r) * (1 + r));
    
    setRetireResult({
      corpus: corpusNeeded,
      monthlySaving,
    });
  };

  const calculateLoan = () => {
    const P = parseFloat(loanAmount);
    const r = parseFloat(loanRate) / 100 / 12;
    const n = parseFloat(loanTenure) * 12;
    
    const emi = P * r * Math.pow(1 + r, n) / (Math.pow(1 + r, n) - 1);
    const totalAmount = emi * n;
    const totalInterest = totalAmount - P;
    
    setLoanResult({
      emi,
      totalInterest,
      totalAmount,
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-3xl font-serif font-bold text-foreground mb-2">Financial Calculators</h1>
        <p className="text-muted-foreground">Plan your financial future with our calculators</p>
      </div>

      <Tabs defaultValue="sip" className="w-full">
        <TabsList className="grid w-full grid-cols-3 mb-8">
          <TabsTrigger value="sip" className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            SIP Calculator
          </TabsTrigger>
          <TabsTrigger value="retirement" className="flex items-center gap-2">
            <PiggyBank className="h-4 w-4" />
            Retirement
          </TabsTrigger>
          <TabsTrigger value="loan" className="flex items-center gap-2">
            <Home className="h-4 w-4" />
            Loan EMI
          </TabsTrigger>
        </TabsList>

        <TabsContent value="sip">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="font-serif flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-accent" />
                  SIP Calculator
                </CardTitle>
                <CardDescription>Calculate your SIP returns</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="sipMonthly">Monthly Investment ($)</Label>
                  <Input
                    id="sipMonthly"
                    type="number"
                    value={sipMonthly}
                    onChange={(e) => setSipMonthly(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="sipRate">Expected Annual Return (%)</Label>
                  <Input
                    id="sipRate"
                    type="number"
                    value={sipRate}
                    onChange={(e) => setSipRate(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="sipYears">Investment Period (Years)</Label>
                  <Input
                    id="sipYears"
                    type="number"
                    value={sipYears}
                    onChange={(e) => setSipYears(e.target.value)}
                  />
                </div>
                <Button onClick={calculateSIP} className="w-full bg-accent hover:bg-accent/90">
                  <Calculator className="h-4 w-4 mr-2" />
                  Calculate
                </Button>
              </CardContent>
            </Card>

            {sipResult && (
              <Card className="border-0 shadow-lg bg-gradient-to-br from-accent/5 to-accent/10">
                <CardHeader>
                  <CardTitle className="font-serif">Results</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="p-4 rounded-lg bg-card">
                    <p className="text-sm text-muted-foreground mb-1">Total Invested</p>
                    <p className="text-2xl font-bold font-serif">{formatCurrency(sipResult.invested)}</p>
                  </div>
                  <div className="p-4 rounded-lg bg-card">
                    <p className="text-sm text-muted-foreground mb-1">Estimated Returns</p>
                    <p className="text-2xl font-bold font-serif text-emerald">{formatCurrency(sipResult.returns)}</p>
                  </div>
                  <div className="p-4 rounded-lg bg-accent text-accent-foreground">
                    <p className="text-sm opacity-80 mb-1">Total Value</p>
                    <p className="text-3xl font-bold font-serif">{formatCurrency(sipResult.total)}</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value="retirement">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="font-serif flex items-center gap-2">
                  <PiggyBank className="h-5 w-5 text-accent" />
                  Retirement Calculator
                </CardTitle>
                <CardDescription>Plan for your retirement</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="currentAge">Current Age</Label>
                    <Input
                      id="currentAge"
                      type="number"
                      value={currentAge}
                      onChange={(e) => setCurrentAge(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="retireAge">Retirement Age</Label>
                    <Input
                      id="retireAge"
                      type="number"
                      value={retireAge}
                      onChange={(e) => setRetireAge(e.target.value)}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="monthlyExpense">Current Monthly Expenses ($)</Label>
                  <Input
                    id="monthlyExpense"
                    type="number"
                    value={monthlyExpense}
                    onChange={(e) => setMonthlyExpense(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="inflationRate">Expected Inflation (%)</Label>
                  <Input
                    id="inflationRate"
                    type="number"
                    value={inflationRate}
                    onChange={(e) => setInflationRate(e.target.value)}
                  />
                </div>
                <Button onClick={calculateRetirement} className="w-full bg-accent hover:bg-accent/90">
                  <Calculator className="h-4 w-4 mr-2" />
                  Calculate
                </Button>
              </CardContent>
            </Card>

            {retireResult && (
              <Card className="border-0 shadow-lg bg-gradient-to-br from-accent/5 to-accent/10">
                <CardHeader>
                  <CardTitle className="font-serif">Results</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="p-4 rounded-lg bg-card">
                    <p className="text-sm text-muted-foreground mb-1">Retirement Corpus Needed</p>
                    <p className="text-2xl font-bold font-serif">{formatCurrency(retireResult.corpus)}</p>
                  </div>
                  <div className="p-4 rounded-lg bg-accent text-accent-foreground">
                    <p className="text-sm opacity-80 mb-1">Monthly Savings Required</p>
                    <p className="text-3xl font-bold font-serif">{formatCurrency(retireResult.monthlySaving)}</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value="loan">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="font-serif flex items-center gap-2">
                  <Home className="h-5 w-5 text-accent" />
                  Loan EMI Calculator
                </CardTitle>
                <CardDescription>Calculate your loan EMI</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="loanAmount">Loan Amount ($)</Label>
                  <Input
                    id="loanAmount"
                    type="number"
                    value={loanAmount}
                    onChange={(e) => setLoanAmount(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="loanRate">Interest Rate (%)</Label>
                  <Input
                    id="loanRate"
                    type="number"
                    value={loanRate}
                    onChange={(e) => setLoanRate(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="loanTenure">Loan Tenure (Years)</Label>
                  <Input
                    id="loanTenure"
                    type="number"
                    value={loanTenure}
                    onChange={(e) => setLoanTenure(e.target.value)}
                  />
                </div>
                <Button onClick={calculateLoan} className="w-full bg-accent hover:bg-accent/90">
                  <Calculator className="h-4 w-4 mr-2" />
                  Calculate
                </Button>
              </CardContent>
            </Card>

            {loanResult && (
              <Card className="border-0 shadow-lg bg-gradient-to-br from-accent/5 to-accent/10">
                <CardHeader>
                  <CardTitle className="font-serif">Results</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="p-4 rounded-lg bg-accent text-accent-foreground">
                    <p className="text-sm opacity-80 mb-1">Monthly EMI</p>
                    <p className="text-3xl font-bold font-serif">{formatCurrency(loanResult.emi)}</p>
                  </div>
                  <div className="p-4 rounded-lg bg-card">
                    <p className="text-sm text-muted-foreground mb-1">Total Interest</p>
                    <p className="text-2xl font-bold font-serif text-coral">{formatCurrency(loanResult.totalInterest)}</p>
                  </div>
                  <div className="p-4 rounded-lg bg-card">
                    <p className="text-sm text-muted-foreground mb-1">Total Amount Payable</p>
                    <p className="text-2xl font-bold font-serif">{formatCurrency(loanResult.totalAmount)}</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Calculators;
