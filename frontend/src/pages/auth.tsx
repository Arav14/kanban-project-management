"use client";
import { useState } from "react";
import { useRouter } from "next/router"; // ✅ Pages Router
import { api } from "@/services/api";

export default function AuthPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [form, setForm] = useState({ email: "", password: "", full_name: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setError("");
    setLoading(true);
    try {
      let tokens;
      if (mode === "register") {
        tokens = await api.auth.register(
          form.email,
          form.full_name,
          form.password,
        );
      } else {
        tokens = await api.auth.login(form.email, form.password);
      }
      localStorage.setItem("access_token", tokens.access_token);
      localStorage.setItem("refresh_token", tokens.refresh_token);
      router.push("/dashboard");
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="bg-white rounded-2xl border border-gray-200 p-8 w-full max-w-sm shadow-sm">
        <div className="mb-6">
          <h1 className="text-xl font-semibold text-gray-900">
            {mode === "login" ? "Welcome Back" : "Create account"}
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            {mode === "login"
              ? "Sign in to your workspace"
              : "Start your free workspace"}
          </p>
        </div>
        <div className="flex flex-col gap-3">
          {mode === "register" && (
            <input
              placeholder="Full name"
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              className="border vorder-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400 w-full"
            />
          )}
          <input
            type="email"
            placeholder="Email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400 w-full"
          />
          <input
            type="password"
            placeholder="Password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400 w-full"
          />

          {error && <p className="text-xs text-red-500">{error}</p>}

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="bg-blue-500 text-white text-sm rounded-lg py-2 font-medium hover:bg-blue-600 disabled:opacity-50 transition-colors"
          >
            {loading
              ? "Loading..."
              : mode === "login"
                ? "sign in"
                : "Create account"}
          </button>
        </div>

        <p className="text-xs text-gray-400 text-center mt-4">
          {mode === "login" ? "No account ?" : "Already have one ?"}{" "}
          <button
            onClick={() => setMode(mode === "login" ? "register" : "login")}
            className="text-blue-500 hover:underline"
          >
            {mode === "login" ? "Register" : "Sign in"}
          </button>
        </p>
      </div>
    </div>
  );
}
