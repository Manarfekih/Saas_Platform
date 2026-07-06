import {
  createContext,
  useContext,
  useState,
  useEffect,
} from "react";
import type { ReactNode } from "react";
import api from "../api/auth";

type AuthContextType = {
  token: string | null;
  userEmail: string | null;
  login: (token: string) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType>(
  {} as AuthContextType
);

export const AuthProvider = ({
  children,
}: {
  children: ReactNode;
}) => {
  const [token, setToken] = useState<string | null>(
    localStorage.getItem("token")
  );
  const [userEmail, setUserEmail] = useState<string | null>(null);

  // Fetch user info when token changes
  useEffect(() => {
    if (!token) {
      setUserEmail(null);
      return;
    }
    api
      .get("/auth/me", {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => {
        setUserEmail(res.data.email);
      })
      .catch(() => {
        // Token is invalid or expired — log out
        setToken(null);
        localStorage.removeItem("token");
        setUserEmail(null);
      });
  }, [token]);

  const login = (newToken: string) => {
    localStorage.setItem("token", newToken);
    setToken(newToken);
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setUserEmail(null);
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        userEmail,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () =>
  useContext(AuthContext);