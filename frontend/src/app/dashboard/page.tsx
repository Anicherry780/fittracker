"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import Navbar from "@/components/Navbar";
import CalorieRing from "@/components/CalorieRing";
import MacroCards from "@/components/MacroCards";
import { Camera, Dumbbell, TrendingUp, Utensils } from "lucide-react";
import Link from "next/link";

interface DailySummary {
  date: string;
  calories_consumed: number;
  calories_burned: number;
  net_calories: number;
  calorie_target: number;
  remaining_calories: number;
  protein_g: number;
  fat_g: number;
  carbs_g: number;
}

interface FoodLog {
  id: string;
  meal_type: string;
  food_name: string;
  calories: number;
  logged_at: string;
}

interface ExerciseLog {
  id: string;
  exercise_type: string;
  duration_min: number;
  calories_burned: number;
  logged_at: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [summary, setSummary] = useState<DailySummary | null>(null);
  const [foodLogs, setFoodLogs] = useState<FoodLog[]>([]);
  const [exerciseLogs, setExerciseLogs] = useState<ExerciseLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
      return;
    }
    loadDashboard();
  }, [router]);

  const loadDashboard = async () => {
    try {
      const [summaryData, foodData, exerciseData] = await Promise.all([
        api.get<DailySummary>("/dashboard/today"),
        api.get<FoodLog[]>("/food/log"),
        api.get<ExerciseLog[]>("/exercise/log"),
      ]);
      setSummary(summaryData);
      setFoodLogs(foodData);
      setExerciseLogs(exerciseData);
    } catch (err) {
      console.error("Failed to load dashboard:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <>
        <Navbar />
        <div className="pt-20 flex items-center justify-center min-h-screen">
          <div className="w-8 h-8 border-2 border-[var(--accent-green)] border-t-transparent rounded-full animate-spin" />
        </div>
      </>
    );
  }

  const mealIcons: Record<string, string> = {
    breakfast: "🌅",
    lunch: "☀️",
    dinner: "🌙",
    snack: "🍿",
  };

  return (
    <>
      <Navbar />
      <div className="pt-20 pb-8 px-4 max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold">Today&apos;s Overview</h1>
          <p className="text-sm text-[var(--text-muted)] mt-1">
            {new Date().toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" })}
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Left: Calorie Ring + Macros */}
          <div className="lg:col-span-1 space-y-6">
            <div className="glass-card p-6 glow-green">
              <CalorieRing
                consumed={summary?.calories_consumed || 0}
                target={summary?.calorie_target || 2000}
                burned={summary?.calories_burned || 0}
              />
            </div>
            <MacroCards
              protein={summary?.protein_g || 0}
              fat={summary?.fat_g || 0}
              carbs={summary?.carbs_g || 0}
            />
          </div>

          {/* Right: Quick Actions + Logs */}
          <div className="lg:col-span-2 space-y-6">
            {/* Quick Actions */}
            <div className="grid grid-cols-2 gap-3">
              <Link
                href="/food-scanner"
                className="glass-card p-5 flex items-center gap-3 hover:scale-[1.02] transition-transform cursor-pointer"
              >
                <div className="w-10 h-10 rounded-xl bg-[var(--accent-green)]/10 flex items-center justify-center">
                  <Camera className="w-5 h-5 text-[var(--accent-green)]" />
                </div>
                <div>
                  <p className="font-semibold text-sm">Scan Food</p>
                  <p className="text-xs text-[var(--text-muted)]">AI-powered detection</p>
                </div>
              </Link>
              <Link
                href="/workout"
                className="glass-card p-5 flex items-center gap-3 hover:scale-[1.02] transition-transform cursor-pointer"
              >
                <div className="w-10 h-10 rounded-xl bg-[var(--accent-lime)]/10 flex items-center justify-center">
                  <Dumbbell className="w-5 h-5 text-[var(--accent-lime)]" />
                </div>
                <div>
                  <p className="font-semibold text-sm">Log Workout</p>
                  <p className="text-xs text-[var(--text-muted)]">Track exercise</p>
                </div>
              </Link>
            </div>

            {/* Today's Meals */}
            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-semibold flex items-center gap-2">
                  <Utensils className="w-4 h-4 text-[var(--accent-green)]" />
                  Today&apos;s Meals
                </h2>
                <Link href="/food-log" className="text-xs text-[var(--accent-green)] hover:underline">
                  View all
                </Link>
              </div>
              {foodLogs.length === 0 ? (
                <p className="text-sm text-[var(--text-muted)] text-center py-6">
                  No meals logged yet today. Scan or add your first meal!
                </p>
              ) : (
                <div className="space-y-2">
                  {foodLogs.slice(0, 5).map((log) => (
                    <div
                      key={log.id}
                      className="flex items-center justify-between py-2 px-3 rounded-xl bg-[var(--bg-secondary)]"
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-lg">{mealIcons[log.meal_type] || "🍽️"}</span>
                        <div>
                          <p className="text-sm font-medium">{log.food_name}</p>
                          <p className="text-xs text-[var(--text-muted)] capitalize">{log.meal_type}</p>
                        </div>
                      </div>
                      <span className="text-sm font-semibold text-[var(--accent-green)]">
                        {Math.round(log.calories)} kcal
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Today's Exercises */}
            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-semibold flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-[var(--accent-lime)]" />
                  Today&apos;s Exercises
                </h2>
                <Link href="/workout" className="text-xs text-[var(--accent-green)] hover:underline">
                  Log more
                </Link>
              </div>
              {exerciseLogs.length === 0 ? (
                <p className="text-sm text-[var(--text-muted)] text-center py-6">
                  No exercises logged yet. Start your workout!
                </p>
              ) : (
                <div className="space-y-2">
                  {exerciseLogs.map((log) => (
                    <div
                      key={log.id}
                      className="flex items-center justify-between py-2 px-3 rounded-xl bg-[var(--bg-secondary)]"
                    >
                      <div>
                        <p className="text-sm font-medium capitalize">
                          {log.exercise_type.replace(/_/g, " ")}
                        </p>
                        <p className="text-xs text-[var(--text-muted)]">{log.duration_min} min</p>
                      </div>
                      <span className="text-sm font-semibold text-[var(--accent-lime)]">
                        -{Math.round(log.calories_burned)} kcal
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
