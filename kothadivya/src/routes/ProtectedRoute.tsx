import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { Loader2 } from "lucide-react";

const ProtectedRoute = () => {
  const { user, loading } = useAuth();

  // While checking auth state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    );
  }

  // If not logged in → go to auth
  if (!user) {
    return <Navigate to="/auth" replace />;
  }

  // Logged in → allow access
  return <Outlet />;
};

export default ProtectedRoute;
