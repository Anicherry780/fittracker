"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { logout, getUser } from "@/lib/auth";
import {
  LayoutDashboard, Camera, UtensilsCrossed, Dumbbell,
  User, LogOut, Menu, X, Flame
} from "lucide-react";
import { useState } from "react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/food-scanner", label: "Food Scanner", icon: Camera },
  { href: "/food-log", label: "Food Log", icon: UtensilsCrossed },
  { href: "/workout", label: "Workout", icon: Dumbbell },
  { href: "/profile", label: "Profile", icon: User },
];

export default function Navbar() {
  const pathname = usePathname();
  const user = getUser();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass-card border-b border-[var(--border-color)] px-4 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Logo */}
        <Link href="/dashboard" className="flex items-center gap-2 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[var(--accent-green)] to-[var(--accent-emerald)] flex items-center justify-center">
            <Flame className="w-5 h-5 text-[var(--bg-primary)]" />
          </div>
          <span className="text-xl font-bold gradient-text hidden sm:block">FitTracker</span>
        </Link>

        {/* Desktop Nav */}
        <div className="hidden md:flex items-center gap-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all
                  ${isActive
                    ? "bg-[var(--accent-green)]/10 text-[var(--accent-green)]"
                    : "text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card)]"
                  }`}
              >
                <Icon className="w-4 h-4" />
                {item.label}
              </Link>
            );
          })}
        </div>

        {/* User / Logout */}
        <div className="hidden md:flex items-center gap-3">
          {user && (
            <span className="text-sm text-[var(--text-secondary)]">
              Hey, <span className="text-[var(--accent-green)] font-medium">{user.username}</span>
            </span>
          )}
          <button onClick={logout} className="btn-secondary !py-2 !px-3 flex items-center gap-1.5 text-sm">
            <LogOut className="w-4 h-4" />
            Logout
          </button>
        </div>

        {/* Mobile Menu Toggle */}
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="md:hidden p-2 rounded-xl text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
        >
          {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {/* Mobile Menu */}
      {mobileOpen && (
        <div className="md:hidden mt-3 pb-3 border-t border-[var(--border-color)] pt-3 space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileOpen(false)}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all
                  ${isActive
                    ? "bg-[var(--accent-green)]/10 text-[var(--accent-green)]"
                    : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                  }`}
              >
                <Icon className="w-5 h-5" />
                {item.label}
              </Link>
            );
          })}
          <button
            onClick={logout}
            className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-[var(--danger)] w-full"
          >
            <LogOut className="w-5 h-5" />
            Logout
          </button>
        </div>
      )}
    </nav>
  );
}
