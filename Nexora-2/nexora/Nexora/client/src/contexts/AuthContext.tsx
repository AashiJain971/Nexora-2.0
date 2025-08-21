import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { useLocation } from "wouter";

interface User {
  id: string;
  email: string;
  full_name: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string, userData: User) => void;
  logout: () => void;
  refreshToken: () => Promise<string | null>;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [, setLocation] = useLocation();

  useEffect(() => {
    // Check for existing auth data on app load
    const storedToken = localStorage.getItem("nexora_token");
    const storedUser = localStorage.getItem("nexora_user");

    if (storedToken && storedUser) {
      try {
        const userData = JSON.parse(storedUser);
        setToken(storedToken);
        setUser(userData);
        console.log("🔐 Restored user session:", userData.email);

        // Verify token is still valid by testing it
        verifyTokenAndRefresh(storedToken);
      } catch (error) {
        // Clear invalid data
        localStorage.removeItem("nexora_token");
        localStorage.removeItem("nexora_user");
        console.log("🔐 Cleared invalid auth data");
        createDemoUser();
      }
    } else {
      // For development: Auto-register a demo user if no authentication exists
      console.log("🔐 No existing auth found, creating demo user...");
      createDemoUser();
    }
    setIsLoading(false);
  }, []);

  const verifyTokenAndRefresh = async (currentToken: string) => {
    try {
      // Test the token by making a simple API call
      const response = await fetch("https://nexora-2-0-6.onrender.com/", {
        headers: {
          Authorization: `Bearer ${currentToken}`,
        },
      });

      // If the API is not available or token is expired, refresh it
      if (
        !response.ok &&
        (response.status === 401 || response.status === 403)
      ) {
        console.log("🔄 Token expired or invalid, refreshing...");
        await refreshToken();
      }
    } catch (error) {
      console.log("🔄 Could not verify token, refreshing...");
      await refreshToken();
    }
  };

  const createDemoUser = async () => {
    try {
      // Check if user already exists by trying login first
      console.log("🔐 Attempting demo user authentication...");

      const loginResponse = await fetch(
        "https://nexora-2-0-6.onrender.com/login",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: "demo@nexora.com",
            password: "demo123",
          }),
        }
      );

      if (loginResponse.ok) {
        const loginResult = await loginResponse.json();
        setToken(loginResult.access_token);
        setUser(loginResult.user_data);
        localStorage.setItem("nexora_token", loginResult.access_token);
        localStorage.setItem(
          "nexora_user",
          JSON.stringify(loginResult.user_data)
        );
        console.log(
          "✅ Demo user authenticated successfully:",
          loginResult.user_data
        );
        return;
      }

      // If login fails, try to register new demo user
      console.log("🆕 Demo user not found, creating new user...");
      const response = await fetch(
        "https://nexora-2-0-6.onrender.com/register",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            full_name: "Demo User",
            email: "demo@nexora.com",
            password: "demo123",
          }),
        }
      );

      const result = await response.json();

      if (response.ok) {
        setToken(result.access_token);
        setUser(result.user_data);
        localStorage.setItem("nexora_token", result.access_token);
        localStorage.setItem("nexora_user", JSON.stringify(result.user_data));
        console.log(
          "✅ Demo user created and authenticated:",
          result.user_data
        );
      } else {
        console.warn(
          "⚠️ Demo user registration failed, but login should have worked"
        );
        console.warn("Registration error:", result);
      }
    } catch (error) {
      console.error("❌ Error with demo user authentication:", error);
    }
  };

  const refreshToken = async () => {
    try {
      console.log("🔄 Refreshing authentication token...");
      const loginResponse = await fetch(
        "https://nexora-2-0-6.onrender.com/login",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: "demo@nexora.com",
            password: "demo123",
          }),
        }
      );

      if (loginResponse.ok) {
        const loginResult = await loginResponse.json();
        setToken(loginResult.access_token);
        setUser(loginResult.user_data);
        localStorage.setItem("nexora_token", loginResult.access_token);
        localStorage.setItem(
          "nexora_user",
          JSON.stringify(loginResult.user_data)
        );
        console.log("✅ Token refreshed successfully");
        return loginResult.access_token;
      } else {
        console.error("❌ Failed to refresh token");
        logout();
        return null;
      }
    } catch (error) {
      console.error("❌ Error refreshing token:", error);
      logout();
      return null;
    }
  };

  const login = (newToken: string, userData: User) => {
    setToken(newToken);
    setUser(userData);
    localStorage.setItem("nexora_token", newToken);
    localStorage.setItem("nexora_user", JSON.stringify(userData));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem("nexora_token");
    localStorage.removeItem("nexora_user");
    setLocation("/");
  };

  const value = {
    user,
    token,
    login,
    logout,
    refreshToken,
    isAuthenticated: !!token && !!user,
    isLoading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
