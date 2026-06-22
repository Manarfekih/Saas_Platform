import { useState } from "react";
import api from "../api/auth";
import { Link, useNavigate } from "react-router-dom";

export default function RegisterPage() {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);

  const handleRegister = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

    try {
      setLoading(true);

      await api.post("/auth/register", {
        name,
        email,
        password,
      });

      navigate("/login");
    } catch (error) {
      alert("Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <form
        onSubmit={handleRegister}
        className="bg-white p-8 rounded-lg shadow-md w-96"
      >
        <h1 className="text-3xl font-bold mb-6 text-center">
          Create Account
        </h1>

        <input
          placeholder="Name"
          className="border p-3 w-full mb-4 rounded"
          value={name}
          onChange={(e) =>
            setName(e.target.value)
          }
        />

        <input
          placeholder="Email"
          className="border p-3 w-full mb-4 rounded"
          value={email}
          onChange={(e) =>
            setEmail(e.target.value)
          }
        />

        <input
          type="password"
          placeholder="Password"
          className="border p-3 w-full mb-4 rounded"
          value={password}
          onChange={(e) =>
            setPassword(e.target.value)
          }
        />

        <button
          disabled={loading}
          className="bg-black text-white w-full p-3 rounded"
        >
          {loading
            ? "Creating..."
            : "Create Account"}
        </button>

        <p className="mt-4 text-center">
          Already have an account?
          <Link
            className="text-blue-600 ml-2"
            to="/login"
          >
            Sign In
          </Link>
        </p>
      </form>
    </div>
  );
}