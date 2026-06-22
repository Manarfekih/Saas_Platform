import { useState } from "react";
import api from "../api/auth";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const navigate = useNavigate();

  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const handleLogin = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

    try {
      setLoading(true);

      const response = await api.post(
        "/auth/login",
        {
          email,
          password,
        }
      );

      login(
        response.data.access_token
      );

      navigate("/documents");
    } catch {
      alert("Invalid credentials");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex justify-center items-center bg-gray-100">
      <form
        onSubmit={handleLogin}
        className="bg-white p-8 rounded-lg shadow-md w-96"
      >
        <h1 className="text-3xl font-bold mb-6 text-center">
          Sign In
        </h1>

        <input
          className="border p-3 w-full mb-4 rounded"
          placeholder="Email"
          value={email}
          onChange={(e) =>
            setEmail(e.target.value)
          }
        />

        <input
          type="password"
          className="border p-3 w-full mb-4 rounded"
          placeholder="Password"
          value={password}
          onChange={(e) =>
            setPassword(e.target.value)
          }
        />

        <button
          className="bg-black text-white w-full p-3 rounded"
        >
          {loading
            ? "Signing In..."
            : "Sign In"}
        </button>

        <p className="text-center mt-4">
          No account?
          <Link
            to="/register"
            className="text-blue-600 ml-2"
          >
            Create One
          </Link>
        </p>
      </form>
    </div>
  );
}