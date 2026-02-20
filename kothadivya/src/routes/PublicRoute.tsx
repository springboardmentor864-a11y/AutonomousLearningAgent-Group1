import { Navigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";

const PublicRoute = ({ children }: { children: JSX.Element }) => {
  const { user, loading } = useAuth();

  if (loading) return null;

  // Already logged in → dashboard
  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

export default PublicRoute;
