"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { setAuth } from "@/lib/auth";
import { Flame, Eye, EyeOff, Check, X } from "lucide-react";

export default function RegisterPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Password validation rules
  const rules = [
    { label: "At least 8 characters", valid: password.length >= 8 },
    { label: "One uppercase letter", valid: /[A-Z]/.test(password) },
    { label: "One number", valid: /[0-9]/.test(password) },
    { label: "One special character", valid: /[!@#$%^&*(),.?":{}|<>]/.test(password) },
  ];
  const allValid = rules.every((r) => r.valid);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!allValid) return;
    setError("");
    setLoading(true);

    try {
      const data = await api.post<{ access_token: string; user: any }>("/auth/register", {
        username,
        email,
        password,
      });
      setAuth(data.access_token, data.user);
      router.push("/profile");
    } catch (err: any) {
      setError(err.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <div className="glass-card w-full max-w-md p-8 animate-fade-in">
        <div className="flex flex-col items-center gap-3 mb-8">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[var(--accent-green)] to-[var(--accent-emerald)] flex items-center justify-center">
            <Flame className="w-6 h-6 text-[var(--bg-primary)]" />
          </div>
          <h1 className="text-2xl font-bold">Create account</h1>
          <p className="text-sm text-[var(--text-muted)]">Start tracking your fitness journey</p>
        </div>

        <form onSubmit={handleRegister} className="space-y-4">
          <div>
            <label className="text-sm text-[var(--text-secondary)] mb-1.5 block">Username</label>
            <input
              type="text"
              className="input-field"
              placeholder="Choose a username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              minLength={3}
            />
          </div>
          <div>
            <label className="text-sm text-[var(--text-secondary)] mb-1.5 block">Email</label>
            <input
              type="email"
              className="input-field"
              placeholder="your@email.com (for password reset only)"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="text-sm text-[var(--text-secondary)] mb-1.5 block">Password</label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                className="input-field !pr-10"
                placeholder="Create a strong password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            {/* Password rules */}
            {password.length > 0 && (
              <div className="mt-3 space-y-1.5">
                {rules.map((rule) => (
                  <div key={rule.label} className="flex items-center gap-2 text-xs">
                    {rule.valid ? (
                      <Check className="w-3.5 h-3.5 text-[var(--accent-green)]" />
                    ) : (
                      <X className="w-3.5 h-3.5 text-[var(--danger)]" />
                    )}
                    <span className={rule.valid ? "text-[var(--accent-green)]" : "text-[var(--text-muted)]"}>
                      {rule.label}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {error && (
            <p className="text-sm text-[var(--danger)] bg-[var(--danger)]/10 px-4 py-2 rounded-xl">{error}</p>
          )}

          <button
            type="submit"
            className="btn-primary w-full !py-3"
            disabled={loading || !allValid}
          >
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-[var(--text-muted)]">
          Already have an account?{" "}
          <Link href="/login" className="text-[var(--accent-green)] hover:underline font-medium">
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}
