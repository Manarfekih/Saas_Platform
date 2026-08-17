import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from "react";
import type { ReactNode } from "react";
import api from "../api/auth";

type AuthContextType = {
  token: string | null;
  userEmail: string | null;
  userName: string | null;
  profileImage: string | null;
  login: (token: string) => void;
  logout: () => void;
  refreshUser: () => Promise<void>;
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
  const [userName, setUserName] = useState<string | null>(null);
  const [profileImage, setProfileImage] = useState<string | null>(null);

  const fetchUser = useCallback(async () => {
    if (!token) {
      setUserEmail(null);
      setUserName(null);
      setProfileImage(null);
      return;
    }

    try {
      const res = await api.get("/auth/me", {
        headers: { Authorization: `Bearer ${token}` },
      });

      setUserEmail(res.data.email);
      setUserName(res.data.name);
      setProfileImage(res.data.profile_image ?? null);
    } catch {
      // Token is invalid or expired - log out
      setToken(null);
      localStorage.removeItem("token");
      setUserEmail(null);
      setUserName(null);
      setProfileImage(null);
    }
  }, [token]);

  // Fetch user info when token changes
  useEffect(() => {
    void fetchUser();
  }, [fetchUser]);

  const login = (newToken: string) => {
    localStorage.setItem("token", newToken);
    setToken(newToken);
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setUserEmail(null);
    setUserName(null);
    setProfileImage(null);
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        userEmail,
        userName,
        profileImage,
        login,
        logout,
        refreshUser: fetchUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () =>
  useContext(AuthContext);
