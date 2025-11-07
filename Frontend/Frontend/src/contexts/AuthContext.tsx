import { createContext, useContext, useEffect, useMemo, useState, ReactNode } from "react";
import { apiRequest, ApiError } from "@/lib/api";
import type { ApiUser, AuthResponse } from "@/types/api";

interface AuthContextValue {
  user: ApiUser | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  resetError: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const TOKEN_STORAGE_KEY = "cotizainador.token";
const USER_STORAGE_KEY = "cotizainador.user";

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<ApiUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem(TOKEN_STORAGE_KEY);
    const storedUser = localStorage.getItem(USER_STORAGE_KEY);

    if (storedToken) {
      setToken(storedToken);
      if (storedUser) {
        try {
          const parsed = JSON.parse(storedUser) as ApiUser;
          setUser(parsed);
        } catch {
          localStorage.removeItem(USER_STORAGE_KEY);
        }
      }
    }
    setIsLoading(false);
  }, []);

  const persistSession = (authResponse: AuthResponse) => {
    setToken(authResponse.access_token);
    setUser(authResponse.user);
    localStorage.setItem(TOKEN_STORAGE_KEY, authResponse.access_token);
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(authResponse.user));
  };

  const clearSession = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    localStorage.removeItem(USER_STORAGE_KEY);
  };

  const handleAuth = async (endpoint: "/auth/login" | "/auth/register", payload: Record<string, string>) => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await apiRequest<AuthResponse>(endpoint, {
        method: "POST",
        body: payload,
      });
      persistSession(response);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Unexpected error. Please try again.");
      }
      clearSession();
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      isLoading,
      error,
      login: (email: string, password: string) => handleAuth("/auth/login", { email, password }),
      register: (name: string, email: string, password: string) =>
        handleAuth("/auth/register", { name, email, password }),
      logout: () => {
        clearSession();
      },
      resetError: () => setError(null),
    }),
    [user, token, isLoading, error],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
};
