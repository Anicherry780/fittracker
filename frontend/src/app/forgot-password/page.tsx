"use client";

import { useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { Mail, ArrowLeft, Loader2, CheckCircle } from "lucide-react";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    setLoading(true);
    setError("");

    try {
      await api.post("/auth/forgot-password", { email });
      setSent(true);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="glass-card p-8 w-full max-w-md">
        {sent ? (
          <div className="text-center space-y-4">
            <CheckCircle className="w-12 h-12 text-[var(--accent-green)] mx-auto" />
            <h1 className="text-xl font-bold">Check your email</h1>
            <p className="text-sm text-[var(--text-muted)]">
              If an account with <span className="text-[var(--text-primary)] font-medium">{email}</span> exists,
              we&apos;ve sent a password reset link.
            </p>
            <p className="text-xs text-[var(--text-muted)]">
              Check your spam folder if you don&apos;t see it.
            </p>
            <Link href="/login" className="btn-primary inline-flex items-center gap-2 mt-4">
              <ArrowLeft className="w-4 h-4" /> Back to Login
            </Link>
          </div>
        ) : (
          <>
            <div className="text-center mb-6">
              <div className="w-12 h-12 rounded-2xl bg-[var(--accent-green)]/10 flex items-center justify-center mx-auto mb-3">
                <Mail className="w-6 h-6 text-[var(--accent-green)]" />
              </div>
              <h1 className="text-xl font-bold">Forgot Password?</h1>
              <p className="text-sm text-[var(--text-muted)] mt-1">
                Enter your email and we&apos;ll send you a reset link
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="text-sm text-[var(--text-muted)] mb-1 block">Email</label>
                <input
                  type="email"
                  className="input-field"
                  placeholder="your@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>

              {error && (
                <p className="text-sm text-[var(--danger)] bg-[var(--danger)]/10 px-4 py-2 rounded-lg">{error}</p>
              )}

              <button
                type="submit"
                disabled={loading || !email}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                {loading ? (
                  <><Loader2 className="w-4 h-4 animate-spin" /> Sending...</>
                ) : (
                  "Send Reset Link"
                )}
              </button>
            </form>

            <Link href="/login" className="text-sm text-[var(--text-muted)] hover:text-[var(--accent-green)] flex items-center gap-1 mt-4 justify-center">
              <ArrowLeft className="w-3.5 h-3.5" /> Back to Login
            </Link>
          </>
        )}
      </div>
    </div>
  );
}
