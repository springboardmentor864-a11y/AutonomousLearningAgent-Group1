import { createContext, useContext, useEffect, useState } from "react";
import API from "@/api";

interface User {
  id?: number;
  name?: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<any>;
  signUp: (email: string, password: string, name: string) => Promise<any>;
  signOut: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // 🔹 Load user safely on refresh
  useEffect(() => {
    const storedUser = localStorage.getItem("user");

    if (storedUser && storedUser !== "undefined") {
      try {
        setUser(JSON.parse(storedUser));
      } catch (error) {
        console.error("Invalid user in localStorage");
        localStorage.removeItem("user");
        setUser(null);
      }
    } else {
      setUser(null);
    }

    setLoading(false);
  }, []);

  // 🔹 LOGIN (OAuth2 compatible)
  const signIn = async (email: string, password: string) => {
    try {
      const params = new URLSearchParams();
      params.append("username", email);
      params.append("password", password);

      const res = await API.post("/auth/login", params, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      const userData: User = { email };

      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("user", JSON.stringify(userData));

      setUser(userData);
      return { error: null }; 
    } catch (err: any) {
      const message = err.response?.data?.detail || err.response?.data?.message || err.message || "Login failed";
      return { error: { message } };
    }
  };

  // 🔹 REGISTER
  const signUp = async (email: string, password: string, name: string) => {
    try {
      const res = await API.post("/auth/register", {
        name,
        email,
        password,
      });

      const userData: User = {
        email,
        name,
      };

      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("user", JSON.stringify(userData));

      setUser(userData);
      return { error: null };
    } catch (err: any) {
      return {
        error: err.response?.data || { message: "Signup failed" },
      };
    }
  };

  // 🔹 LOGOUT
  const signOut = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, signIn, signUp, signOut }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return ctx;
};
