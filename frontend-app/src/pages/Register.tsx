import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

export default function Register() {
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ full_name: fullName, email, password }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Registration failed");
      }

      navigate("/login");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-surface text-[var(--foreground)] px-4 transition-colors duration-300">
      <div className="bg-surface-card p-8 rounded-xl shadow-lg w-full max-w-md border border-[var(--border)]">
        <h2 className="text-3xl font-bold mb-6 text-center">Register</h2>
        {error && <div className="text-red-500 mb-4 text-center">{error}</div>}

        <form onSubmit={handleRegister} className="space-y-5">
          <div>
            <label className="block font-medium mb-1">Full Name</label>
            <input
              type="text"
              placeholder="Enter your full name"
              className="w-full border border-[var(--border)] p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 bg-[var(--input)] text-[var(--foreground)] placeholder-gray-500 dark:placeholder-gray-300"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="block font-medium mb-1">Email</label>
            <input
              type="email"
              placeholder="Enter your email"
              className="w-full border border-[var(--border)] p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 bg-[var(--input)] text-[var(--foreground)] placeholder-gray-500 dark:placeholder-gray-300"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="block font-medium mb-1">Password</label>
            <input
              type="password"
              placeholder="Enter your password"
              className="w-full border border-[var(--border)] p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 bg-[var(--input)] text-[var(--foreground)] placeholder-gray-500 dark:placeholder-gray-300"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-green-500 hover:bg-green-600 text-white p-3 rounded-lg font-semibold transition duration-200 disabled:opacity-50"
          >
            {loading ? "Registering..." : "Register"}
          </button>
        </form>

        <p className="mt-6 text-sm text-center text-[var(--muted-foreground)]">
          Already have an account?{" "}
          <Link to="/login" className="text-blue-500 dark:text-blue-500 hover:underline font-medium">
            Login here
          </Link>
        </p>
      </div>
    </div>
  );
}
