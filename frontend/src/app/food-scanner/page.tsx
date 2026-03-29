"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import Navbar from "@/components/Navbar";
import { Camera, Upload, Loader2, Plus, Check, ImageIcon } from "lucide-react";

interface FoodItem {
  name: string;
  calories: number;
  protein_g: number;
  fat_g: number;
  carbs_g: number;
  portion: string | null;
}

interface AnalysisResult {
  foods: FoodItem[];
  image_url: string | null;
  total_calories: number;
  total_protein: number;
  total_fat: number;
  total_carbs: number;
}

export default function FoodScannerPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [mode, setMode] = useState<"idle" | "camera" | "preview">("idle");
  const [preview, setPreview] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState("");
  const [loggedItems, setLoggedItems] = useState<Set<number>>(new Set());
  const [mealType, setMealType] = useState("lunch");

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
    }
  }, [router]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setSelectedFile(file);
    setPreview(URL.createObjectURL(file));
    setMode("preview");
    setResult(null);
    setError("");
    setLoggedItems(new Set());
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setMode("camera");
      }
    } catch {
      setError("Could not access camera. Please use file upload instead.");
    }
  };

  const capturePhoto = () => {
    if (!videoRef.current) return;
    const canvas = document.createElement("canvas");
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    canvas.getContext("2d")?.drawImage(videoRef.current, 0, 0);

    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], "capture.jpg", { type: "image/jpeg" });
        setSelectedFile(file);
        setPreview(canvas.toDataURL("image/jpeg"));
        setMode("preview");
        // Stop camera
        const stream = videoRef.current?.srcObject as MediaStream;
        stream?.getTracks().forEach((t) => t.stop());
      }
    }, "image/jpeg", 0.9);

    setResult(null);
    setLoggedItems(new Set());
  };

  const analyzeFood = async () => {
    if (!selectedFile) return;
    setAnalyzing(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      const data = await api.postForm<AnalysisResult>("/food/analyze", formData);
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Analysis failed. Please try again.");
    } finally {
      setAnalyzing(false);
    }
  };

  const logFoodItem = async (item: FoodItem, index: number) => {
    try {
      await api.post("/food/log", {
        meal_type: mealType,
        food_name: item.name,
        calories: item.calories,
        protein_g: item.protein_g,
        fat_g: item.fat_g,
        carbs_g: item.carbs_g,
        portion: item.portion,
        image_url: result?.image_url,
        detected_by: "ai",
      });
      setLoggedItems((prev) => new Set(prev).add(index));
    } catch (err: any) {
      setError(err.message || "Failed to log food item");
    }
  };

  const reset = () => {
    setMode("idle");
    setPreview(null);
    setSelectedFile(null);
    setResult(null);
    setError("");
    setLoggedItems(new Set());
    const stream = videoRef.current?.srcObject as MediaStream;
    stream?.getTracks().forEach((t) => t.stop());
  };

  return (
    <>
      <Navbar />
      <div className="pt-20 pb-8 px-4 max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold mb-2">AI Food Scanner</h1>
        <p className="text-sm text-[var(--text-muted)] mb-6">
          Upload or capture a food photo for instant nutrition analysis
        </p>

        {/* Mode Selector */}
        {mode === "idle" && (
          <div className="grid grid-cols-2 gap-4 mb-6">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="glass-card p-8 flex flex-col items-center gap-3 hover:scale-[1.02] transition-transform"
            >
              <div className="w-14 h-14 rounded-2xl bg-[var(--accent-green)]/10 flex items-center justify-center">
                <Upload className="w-7 h-7 text-[var(--accent-green)]" />
              </div>
              <p className="font-semibold">Upload Image</p>
              <p className="text-xs text-[var(--text-muted)]">JPG, PNG up to 10MB</p>
            </button>
            <button
              onClick={startCamera}
              className="glass-card p-8 flex flex-col items-center gap-3 hover:scale-[1.02] transition-transform"
            >
              <div className="w-14 h-14 rounded-2xl bg-[var(--accent-lime)]/10 flex items-center justify-center">
                <Camera className="w-7 h-7 text-[var(--accent-lime)]" />
              </div>
              <p className="font-semibold">Use Camera</p>
              <p className="text-xs text-[var(--text-muted)]">Take a live photo</p>
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>
        )}

        {/* Camera View */}
        {mode === "camera" && (
          <div className="glass-card p-4 mb-6">
            <video ref={videoRef} autoPlay playsInline className="w-full rounded-xl" />
            <div className="flex gap-3 mt-4 justify-center">
              <button onClick={capturePhoto} className="btn-primary flex items-center gap-2">
                <Camera className="w-4 h-4" /> Capture
              </button>
              <button onClick={reset} className="btn-secondary">Cancel</button>
            </div>
          </div>
        )}

        {/* Preview + Analysis */}
        {mode === "preview" && preview && (
          <div className="space-y-6">
            <div className="glass-card p-4">
              <img src={preview} alt="Food preview" className="w-full rounded-xl max-h-80 object-cover" />
              <div className="flex gap-3 mt-4">
                {/* Meal type selector */}
                <select
                  value={mealType}
                  onChange={(e) => setMealType(e.target.value)}
                  className="input-field !w-auto"
                >
                  <option value="breakfast">🌅 Breakfast</option>
                  <option value="lunch">☀️ Lunch</option>
                  <option value="dinner">🌙 Dinner</option>
                  <option value="snack">🍿 Snack</option>
                </select>
                <button
                  onClick={analyzeFood}
                  disabled={analyzing}
                  className="btn-primary flex-1 flex items-center justify-center gap-2"
                >
                  {analyzing ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" /> Analyzing...
                    </>
                  ) : (
                    <>
                      <ImageIcon className="w-4 h-4" /> Analyze Food
                    </>
                  )}
                </button>
                <button onClick={reset} className="btn-secondary">New</button>
              </div>
            </div>

            {/* Results */}
            {result && (
              <div className="glass-card p-6 animate-fade-in">
                <h2 className="font-semibold mb-4 text-[var(--accent-green)]">
                  Detected {result.foods.length} item{result.foods.length !== 1 ? "s" : ""}
                </h2>
                <div className="space-y-3">
                  {result.foods.map((food, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-4 rounded-xl bg-[var(--bg-secondary)]"
                    >
                      <div className="flex-1">
                        <p className="font-medium capitalize">{food.name}</p>
                        <p className="text-xs text-[var(--text-muted)] mt-1">
                          {food.portion && <span>{food.portion} · </span>}
                          P: {food.protein_g}g · F: {food.fat_g}g · C: {food.carbs_g}g
                        </p>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-lg font-bold text-[var(--accent-green)]">
                          {Math.round(food.calories)}
                          <span className="text-xs text-[var(--text-muted)] ml-0.5">kcal</span>
                        </span>
                        <button
                          onClick={() => logFoodItem(food, idx)}
                          disabled={loggedItems.has(idx)}
                          className={`w-8 h-8 rounded-lg flex items-center justify-center transition-all ${
                            loggedItems.has(idx)
                              ? "bg-[var(--accent-green)] text-[var(--bg-primary)]"
                              : "bg-[var(--bg-card)] hover:bg-[var(--accent-green)]/20 text-[var(--accent-green)]"
                          }`}
                        >
                          {loggedItems.has(idx) ? <Check className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Totals */}
                <div className="mt-4 pt-4 border-t border-[var(--border-color)] grid grid-cols-4 gap-3 text-center">
                  <div>
                    <p className="text-lg font-bold text-[var(--accent-green)]">{Math.round(result.total_calories)}</p>
                    <p className="text-xs text-[var(--text-muted)]">kcal</p>
                  </div>
                  <div>
                    <p className="text-lg font-bold text-[#3b82f6]">{Math.round(result.total_protein)}</p>
                    <p className="text-xs text-[var(--text-muted)]">Protein</p>
                  </div>
                  <div>
                    <p className="text-lg font-bold text-[#f59e0b]">{Math.round(result.total_fat)}</p>
                    <p className="text-xs text-[var(--text-muted)]">Fat</p>
                  </div>
                  <div>
                    <p className="text-lg font-bold text-[#a3e635]">{Math.round(result.total_carbs)}</p>
                    <p className="text-xs text-[var(--text-muted)]">Carbs</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {error && (
          <p className="text-sm text-[var(--danger)] bg-[var(--danger)]/10 px-4 py-3 rounded-xl mt-4">{error}</p>
        )}
      </div>
    </>
  );
}
