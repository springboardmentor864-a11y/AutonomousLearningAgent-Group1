import { NavLink, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import API from "@/api";
import { useAuth } from "@/contexts/AuthContext";
import {
  LayoutDashboard,
  User,
  Briefcase,
  Target,
  TrendingUp,
  Receipt,
  Lightbulb,
  LogOut,
  Calculator,
  ShieldCheck,
  AlertTriangle,
} from "lucide-react";
import { cn } from "@/lib/utils";

/* ---------------- TYPES ---------------- */
interface Profile {
  id: number;
  name: string;
  email: string;
  kyc_status: "verified" | "unverified";
  risk_profile: "low" | "moderate" | "aggressive" ;
}

const Sidebar = () => {
  const location = useLocation();
  const { signOut } = useAuth();

  const [profile, setProfile] = useState<Profile | null>(null);

  /* -----------------------------------
     FETCH CURRENT USER
  ----------------------------------- */
  useEffect(() => {
    API.get("/auth/me")
      .then((res) => setProfile(res.data))
      .catch(() => {
        console.error("Failed to load user");
      });
  }, []);

  const navItems = [
    { path: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { path: "/profile", label: "Profile", icon: User },
    { path: "/portfolio", label: "Portfolio", icon: Briefcase },
    { path: "/goals", label: "Goals", icon: Target },
    { path: "/investments", label: "Investments", icon: TrendingUp },
    { path: "/transactions", label: "Transactions", icon: Receipt },
    { path: "/recommendations", label: "Recommendations", icon: Lightbulb },
    { path: "/calculators", label: "Calculators", icon: Calculator },
  ];

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-sidebar text-sidebar-foreground flex flex-col z-50">
      {/* Logo */}
      <div className="p-6 border-b border-sidebar-border">
        <h1 className="text-2xl font-serif font-bold">
          Wealth<span className="text-sidebar-primary">Forge</span>
        </h1>
      </div>

      {/* User Info */}
      <div className="p-4 border-b border-sidebar-border space-y-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-sidebar-primary flex items-center justify-center text-sidebar-primary-foreground font-semibold">
            {profile?.name?.charAt(0).toUpperCase() || "U"}
          </div>
          <div className="min-w-0">
            <p className="text-sm font-medium truncate">
              {profile?.name}
            </p>
            <p className="text-xs text-sidebar-foreground/60 truncate">
              {profile?.email || ""}
            </p>
          </div>
        </div>

        {/* KYC + Risk */}
        <div className="flex justify-between text-xs">
          <div className="flex items-center gap-1">
            {profile?.kyc_status === "verified" ? (
              <ShieldCheck className="h-4 w-4 text-green-500" />
            ) : (
              <AlertTriangle className="h-4 w-4 text-yellow-500" />
            )}
            <span className="capitalize">
              {profile?.kyc_status || "pending"}
            </span>
          </div>

          <span className="capitalize text-sidebar-foreground/70">
            Risk: {profile?.risk_profile || "medium"}
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={cn(
              "nav-link",
              location.pathname === item.path && "active"
            )}
          >
            <item.icon className="h-5 w-5" />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Logout */}
      <div className="p-4 border-t border-sidebar-border">
        <button
          onClick={signOut}
          className="nav-link w-full text-sidebar-foreground/70 hover:text-sidebar-foreground"
        >
          <LogOut className="h-5 w-5" />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
