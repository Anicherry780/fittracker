"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import Navbar from "@/components/Navbar";
import { Dumbbell, Flame, Clock, Search, Plus, Trash2 } from "lucide-react";

interface Exercise {
  name: string;
  display_name: string;
  met_value: number;
  category: string;
}

interface ExerciseLog {
  id: string;
  exercise_type: string;
  duration_min: number;
  calories_burned: number;
  reps: number | null;
  sets: number | null;
  logged_at: string;
}

export default function WorkoutPage() {
  const router = useRouter();
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [logs, setLogs] = useState<ExerciseLog[]>([]);
  const [search, setSearch] = useState("");
  const [selectedExercise, setSelectedExercise] = useState("");
  const [duration, setDuration] = useState("30");
  const [reps, setReps] = useState("");
  const [sets, setSets] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeCategory, setActiveCategory] = useState("All");

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
      return;
    }
    loadData();
  }, [router]);

  const loadData = async () => {
    try {
      const [exerciseList, logData] = await Promise.all([
        api.get<Exercise[]>("/exercise/list"),
        api.get<ExerciseLog[]>("/exercise/log"),
      ]);
      setExercises(exerciseList);
      setLogs(logData);
    } catch (err) {
      console.error(err);
    }
  };

  const logExercise = async () => {
    if (!selectedExercise || !duration) return;
    setLoading(true);
    try {
      await api.post("/exercise/log", {
        exercise_type: selectedExercise,
        duration_min: parseFloat(duration),
        reps: reps ? parseInt(reps) : null,
        sets: sets ? parseInt(sets) : null,
      });
      setSelectedExercise("");
      setDuration("30");
      setReps("");
      setSets("");
      await loadData();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const deleteLog = async (id: string) => {
    try {
      await api.delete(`/exercise/log/${id}`);
      setLogs(logs.filter((l) => l.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  const categories = ["All", ...new Set(exercises.map((e) => e.category))];
  const filtered = exercises.filter((e) => {
    const matchSearch = e.display_name.toLowerCase().includes(search.toLowerCase());
    const matchCategory = activeCategory === "All" || e.category === activeCategory;
    return matchSearch && matchCategory;
  });

  const totalBurned = logs.reduce((sum, l) => sum + l.calories_burned, 0);

  return (
    <>
      <Navbar />
      <div className="pt-20 pb-8 px-4 max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">Workout Tracker</h1>
            <p className="text-sm text-[var(--text-muted)]">Log exercises & track calorie burn</p>
          </div>
          <div className="glass-card px-4 py-2 flex items-center gap-2">
            <Flame className="w-4 h-4 text-[var(--accent-lime)]" />
            <span className="font-bold text-[var(--accent-lime)]">{Math.round(totalBurned)}</span>
            <span className="text-xs text-[var(--text-muted)]">kcal burned today</span>
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Log Exercise Form */}
          <div className="glass-card p-6">
            <h2 className="font-semibold mb-4 flex items-center gap-2">
              <Dumbbell className="w-4 h-4 text-[var(--accent-green)]" />
              Log Exercise
            </h2>

            {/* Search */}
            <div className="relative mb-3">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)]" />
              <input
                type="text"
                className="input-field !pl-10"
                placeholder="Search exercises..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>

            {/* Categories */}
            <div className="flex gap-1.5 mb-3 flex-wrap">
              {categories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setActiveCategory(cat)}
                  className={`text-xs px-3 py-1.5 rounded-lg transition-all ${
                    activeCategory === cat
                      ? "bg-[var(--accent-green)] text-[var(--bg-primary)] font-semibold"
                      : "bg-[var(--bg-secondary)] text-[var(--text-muted)] hover:text-[var(--text-primary)]"
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* Exercise List */}
            <div className="max-h-48 overflow-y-auto mb-4 space-y-1">
              {filtered.slice(0, 15).map((ex) => (
                <button
                  key={ex.name}
                  onClick={() => setSelectedExercise(ex.name)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm flex justify-between transition-all ${
                    selectedExercise === ex.name
                      ? "bg-[var(--accent-green)]/10 text-[var(--accent-green)] border border-[var(--accent-green)]/30"
                      : "bg-[var(--bg-secondary)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                  }`}
                >
                  <span>{ex.display_name}</span>
                  <span className="text-xs text-[var(--text-muted)]">MET {ex.met_value}</span>
                </button>
              ))}
            </div>

            {/* Duration + Reps/Sets */}
            <div className="grid grid-cols-3 gap-3 mb-4">
              <div>
                <label className="text-xs text-[var(--text-muted)] mb-1 block">Duration (min)</label>
                <input
                  type="number"
                  className="input-field text-center"
                  value={duration}
                  onChange={(e) => setDuration(e.target.value)}
                  min="1"
                />
              </div>
              <div>
                <label className="text-xs text-[var(--text-muted)] mb-1 block">Reps (optional)</label>
                <input
                  type="number"
                  className="input-field text-center"
                  value={reps}
                  onChange={(e) => setReps(e.target.value)}
                  placeholder="-"
                />
              </div>
              <div>
                <label className="text-xs text-[var(--text-muted)] mb-1 block">Sets (optional)</label>
                <input
                  type="number"
                  className="input-field text-center"
                  value={sets}
                  onChange={(e) => setSets(e.target.value)}
                  placeholder="-"
                />
              </div>
            </div>

            <button
              onClick={logExercise}
              disabled={!selectedExercise || !duration || loading}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              <Plus className="w-4 h-4" />
              {loading ? "Logging..." : "Log Exercise"}
            </button>
          </div>

          {/* Today's Exercise Logs */}
          <div className="glass-card p-6">
            <h2 className="font-semibold mb-4 flex items-center gap-2">
              <Clock className="w-4 h-4 text-[var(--accent-lime)]" />
              Today&apos;s Exercises
            </h2>
            {logs.length === 0 ? (
              <p className="text-sm text-[var(--text-muted)] text-center py-12">
                No exercises logged today yet. Start your workout!
              </p>
            ) : (
              <div className="space-y-2">
                {logs.map((log) => (
                  <div
                    key={log.id}
                    className="flex items-center justify-between p-3 rounded-xl bg-[var(--bg-secondary)]"
                  >
                    <div>
                      <p className="text-sm font-medium capitalize">
                        {log.exercise_type.replace(/_/g, " ")}
                      </p>
                      <p className="text-xs text-[var(--text-muted)]">
                        {log.duration_min} min
                        {log.reps && ` · ${log.reps} reps`}
                        {log.sets && ` · ${log.sets} sets`}
                      </p>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-bold text-[var(--accent-lime)]">
                        -{Math.round(log.calories_burned)} kcal
                      </span>
                      <button
                        onClick={() => deleteLog(log.id)}
                        className="text-[var(--text-muted)] hover:text-[var(--danger)] transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
