"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import Navbar from "@/components/Navbar";
import { UtensilsCrossed, Plus, Trash2, Calendar } from "lucide-react";

interface FoodLog {
  id: string;
  meal_type: string;
  food_name: string;
  calories: number;
  protein_g: number;
  fat_g: number;
  carbs_g: number;
  portion: string | null;
  detected_by: string;
  logged_at: string;
}

export default function FoodLogPage() {
  const router = useRouter();
  const [logs, setLogs] = useState<FoodLog[]>([]);
  const [date, setDate] = useState(new Date().toISOString().split("T")[0]);
  const [showManual, setShowManual] = useState(false);
  const [form, setForm] = useState({
    meal_type: "lunch",
    food_name: "",
    calories: "",
    protein_g: "",
    fat_g: "",
    carbs_g: "",
    portion: "",
  });

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
      return;
    }
    loadLogs();
  }, [date, router]);

  const loadLogs = async () => {
    try {
      const data = await api.get<FoodLog[]>(`/food/log?log_date=${date}`);
      setLogs(data);
    } catch (err) {
      console.error(err);
    }
  };

  const addManual = async () => {
    if (!form.food_name || !form.calories) return;
    try {
      await api.post("/food/log", {
        ...form,
        calories: parseFloat(form.calories),
        protein_g: parseFloat(form.protein_g || "0"),
        fat_g: parseFloat(form.fat_g || "0"),
        carbs_g: parseFloat(form.carbs_g || "0"),
        detected_by: "manual",
      });
      setForm({ meal_type: "lunch", food_name: "", calories: "", protein_g: "", fat_g: "", carbs_g: "", portion: "" });
      setShowManual(false);
      await loadLogs();
    } catch (err) {
      console.error(err);
    }
  };

  const deleteLog = async (id: string) => {
    try {
      await api.delete(`/food/log/${id}`);
      setLogs(logs.filter((l) => l.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  const mealIcons: Record<string, string> = {
    breakfast: "🌅", lunch: "☀️", dinner: "🌙", snack: "🍿",
  };

  const grouped = {
    breakfast: logs.filter((l) => l.meal_type === "breakfast"),
    lunch: logs.filter((l) => l.meal_type === "lunch"),
    dinner: logs.filter((l) => l.meal_type === "dinner"),
    snack: logs.filter((l) => l.meal_type === "snack"),
  };

  const totalCal = logs.reduce((s, l) => s + l.calories, 0);

  return (
    <>
      <Navbar />
      <div className="pt-20 pb-8 px-4 max-w-3xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">Food Log</h1>
            <p className="text-sm text-[var(--text-muted)]">
              Total: <span className="text-[var(--accent-green)] font-semibold">{Math.round(totalCal)} kcal</span>
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)]" />
              <input
                type="date"
                className="input-field !pl-10 !w-auto"
                value={date}
                onChange={(e) => setDate(e.target.value)}
              />
            </div>
            <button onClick={() => setShowManual(!showManual)} className="btn-primary flex items-center gap-1.5">
              <Plus className="w-4 h-4" /> Add
            </button>
          </div>
        </div>

        {/* Manual entry form */}
        {showManual && (
          <div className="glass-card p-6 mb-6 animate-fade-in">
            <h3 className="font-semibold mb-3">Add Food Manually</h3>
            <div className="grid grid-cols-2 gap-3">
              <div className="col-span-2">
                <select
                  className="input-field"
                  value={form.meal_type}
                  onChange={(e) => setForm({ ...form, meal_type: e.target.value })}
                >
                  <option value="breakfast">🌅 Breakfast</option>
                  <option value="lunch">☀️ Lunch</option>
                  <option value="dinner">🌙 Dinner</option>
                  <option value="snack">🍿 Snack</option>
                </select>
              </div>
              <input className="input-field col-span-2" placeholder="Food name" value={form.food_name}
                onChange={(e) => setForm({ ...form, food_name: e.target.value })} />
              <input className="input-field" placeholder="Calories" type="number" value={form.calories}
                onChange={(e) => setForm({ ...form, calories: e.target.value })} />
              <input className="input-field" placeholder="Portion (optional)" value={form.portion}
                onChange={(e) => setForm({ ...form, portion: e.target.value })} />
              <input className="input-field" placeholder="Protein (g)" type="number" value={form.protein_g}
                onChange={(e) => setForm({ ...form, protein_g: e.target.value })} />
              <input className="input-field" placeholder="Fat (g)" type="number" value={form.fat_g}
                onChange={(e) => setForm({ ...form, fat_g: e.target.value })} />
              <input className="input-field" placeholder="Carbs (g)" type="number" value={form.carbs_g}
                onChange={(e) => setForm({ ...form, carbs_g: e.target.value })} />
              <button onClick={addManual} className="btn-primary col-span-1">Save</button>
            </div>
          </div>
        )}

        {/* Grouped by meal */}
        <div className="space-y-4">
          {(["breakfast", "lunch", "dinner", "snack"] as const).map((meal) => {
            const items = grouped[meal];
            if (items.length === 0) return null;
            const mealCal = items.reduce((s, l) => s + l.calories, 0);
            return (
              <div key={meal} className="glass-card p-5">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold capitalize flex items-center gap-2">
                    <span className="text-lg">{mealIcons[meal]}</span> {meal}
                  </h3>
                  <span className="text-sm text-[var(--accent-green)] font-medium">{Math.round(mealCal)} kcal</span>
                </div>
                <div className="space-y-2">
                  {items.map((log) => (
                    <div key={log.id} className="flex items-center justify-between py-2 px-3 rounded-lg bg-[var(--bg-secondary)]">
                      <div>
                        <p className="text-sm font-medium">{log.food_name}</p>
                        <p className="text-xs text-[var(--text-muted)]">
                          {log.portion && `${log.portion} · `}
                          P:{Math.round(log.protein_g)}g F:{Math.round(log.fat_g)}g C:{Math.round(log.carbs_g)}g
                          {log.detected_by === "ai" && " · 🤖 AI"}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold">{Math.round(log.calories)} kcal</span>
                        <button onClick={() => deleteLog(log.id)} className="text-[var(--text-muted)] hover:text-[var(--danger)]">
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        {logs.length === 0 && (
          <div className="glass-card p-12 text-center">
            <UtensilsCrossed className="w-10 h-10 text-[var(--text-muted)] mx-auto mb-3" />
            <p className="text-[var(--text-muted)]">No food logged for this day</p>
          </div>
        )}
      </div>
    </>
  );
}
