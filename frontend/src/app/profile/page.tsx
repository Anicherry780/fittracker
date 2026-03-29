"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { isAuthenticated, getUser, setAuth, getToken } from "@/lib/auth";
import Navbar from "@/components/Navbar";
import { User, Save, Calculator } from "lucide-react";

export default function ProfilePage() {
  const router = useRouter();
  const [weight, setWeight] = useState("");
  const [height, setHeight] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("male");
  const [activityLevel, setActivityLevel] = useState("1.55");
  const [calorieTarget, setCalorieTarget] = useState("");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
      return;
    }
    const user = getUser();
    if (user) {
      setWeight(user.weight_kg?.toString() || "");
      setHeight(user.height_cm?.toString() || "");
      setAge(user.age?.toString() || "");
      setGender(user.gender || "male");
      setActivityLevel(user.activity_level?.toString() || "1.55");
      setCalorieTarget(user.calorie_target?.toString() || "");
    }
  }, [router]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const updated = await api.patch<any>("/auth/profile", {
        weight_kg: weight ? parseFloat(weight) : null,
        height_cm: height ? parseFloat(height) : null,
        age: age ? parseInt(age) : null,
        gender: gender || null,
        activity_level: activityLevel ? parseFloat(activityLevel) : null,
        calorie_target: calorieTarget ? parseInt(calorieTarget) : null,
      });
      const token = getToken();
      if (token) setAuth(token, updated);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  // Estimate TDEE
  const estimateTDEE = () => {
    if (!weight || !height || !age) return null;
    const w = parseFloat(weight);
    const h = parseFloat(height);
    const a = parseInt(age);
    const al = parseFloat(activityLevel);
    const bmr =
      gender === "male"
        ? 88.362 + 13.397 * w + 4.799 * h - 5.677 * a
        : 447.593 + 9.247 * w + 3.098 * h - 4.33 * a;
    return Math.round(bmr * al);
  };

  const tdee = estimateTDEE();

  return (
    <>
      <Navbar />
      <div className="pt-20 pb-8 px-4 max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold mb-2">Profile Settings</h1>
        <p className="text-sm text-[var(--text-muted)] mb-6">
          Set your body metrics for accurate calorie calculations
        </p>

        <div className="glass-card p-6 space-y-5">
          <div className="flex items-center gap-3 pb-4 border-b border-[var(--border-color)]">
            <div className="w-10 h-10 rounded-xl bg-[var(--accent-green)]/10 flex items-center justify-center">
              <User className="w-5 h-5 text-[var(--accent-green)]" />
            </div>
            <div>
              <p className="font-semibold">{getUser()?.username}</p>
              <p className="text-xs text-[var(--text-muted)]">{getUser()?.email}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-[var(--text-secondary)] mb-1.5 block">Weight (kg)</label>
              <input
                type="number"
                className="input-field"
                placeholder="70"
                value={weight}
                onChange={(e) => setWeight(e.target.value)}
              />
            </div>
            <div>
              <label className="text-sm text-[var(--text-secondary)] mb-1.5 block">Height (cm)</label>
              <input
                type="number"
                className="input-field"
                placeholder="170"
                value={height}
                onChange={(e) => setHeight(e.target.value)}
              />
            </div>
            <div>
              <label className="text-sm text-[var(--text-secondary)] mb-1.5 block">Age</label>
              <input
                type="number"
                className="input-field"
                placeholder="25"
                value={age}
                onChange={(e) => setAge(e.target.value)}
              />
            </div>
            <div>
              <label className="text-sm text-[var(--text-secondary)] mb-1.5 block">Gender</label>
              <select
                className="input-field"
                value={gender}
                onChange={(e) => setGender(e.target.value)}
              >
                <option value="male">Male</option>
                <option value="female">Female</option>
              </select>
            </div>
          </div>

          <div>
            <label className="text-sm text-[var(--text-secondary)] mb-1.5 block">Activity Level</label>
            <select
              className="input-field"
              value={activityLevel}
              onChange={(e) => setActivityLevel(e.target.value)}
            >
              <option value="1.2">Sedentary (little/no exercise)</option>
              <option value="1.375">Lightly active (1-3 days/week)</option>
              <option value="1.55">Moderately active (3-5 days/week)</option>
              <option value="1.725">Very active (6-7 days/week)</option>
              <option value="1.9">Extra active (athlete/physical job)</option>
            </select>
          </div>

          <div>
            <label className="text-sm text-[var(--text-secondary)] mb-1.5 block">
              Custom Calorie Target (optional)
            </label>
            <input
              type="number"
              className="input-field"
              placeholder={tdee ? `Auto: ${tdee} kcal (from TDEE)` : "Leave blank to use TDEE"}
              value={calorieTarget}
              onChange={(e) => setCalorieTarget(e.target.value)}
            />
          </div>

          {/* TDEE Display */}
          {tdee && (
            <div className="bg-[var(--accent-green)]/5 border border-[var(--accent-green)]/20 rounded-xl p-4 flex items-center gap-3">
              <Calculator className="w-5 h-5 text-[var(--accent-green)]" />
              <div>
                <p className="text-sm font-medium">
                  Estimated TDEE: <span className="text-[var(--accent-green)]">{tdee} kcal/day</span>
                </p>
                <p className="text-xs text-[var(--text-muted)]">
                  Based on Harris-Benedict equation with your activity level
                </p>
              </div>
            </div>
          )}

          <button
            onClick={handleSave}
            disabled={saving}
            className="btn-primary w-full flex items-center justify-center gap-2"
          >
            {saved ? (
              <>Saved!</>
            ) : saving ? (
              <>Saving...</>
            ) : (
              <>
                <Save className="w-4 h-4" /> Save Profile
              </>
            )}
          </button>
        </div>
      </div>
    </>
  );
}
