import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";

import ProtectedRoute from "@/routes/ProtectedRoute";
import PublicRoute from "@/routes/PublicRoute";

import Index from "./pages/Index";
import Auth from "./pages/Auth";
import Dashboard from "./pages/Dashboard";
import Profile from "./pages/Profile";
import Portfolio from "./pages/Portfolio";
import Goals from "./pages/Goals";
import Investments from "./pages/Investments";
import Transactions from "./pages/Transactions";
import Recommendations from "./pages/Recommendations";
import Calculators from "./pages/Calculators";
import DashboardLayout from "./components/layout/DashboardLayout";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />

        <BrowserRouter>
          <AuthProvider>
            <Routes>
              {/* 🌍 Public pages */}
              <Route path="/" element={<Index />} />

              <Route
                path="/auth"
                element={
                  <PublicRoute>
                    <Auth />
                  </PublicRoute>
                }
              />

              {/* 🔐 Protected pages */}
              <Route element={<ProtectedRoute />}>
                <Route element={<DashboardLayout />}>
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/profile" element={<Profile />} />
                  <Route path="/portfolio" element={<Portfolio />} />
                  <Route path="/goals" element={<Goals />} />
                  <Route path="/investments" element={<Investments />} />
                  <Route path="/transactions" element={<Transactions />} />
                  <Route path="/recommendations" element={<Recommendations />} />
                  <Route path="/calculators" element={<Calculators />} />
                </Route>
              </Route>

              {/* ❌ Not found */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </AuthProvider>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
};

export default App;
