"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import Navbar from "@/components/Navbar";
import { Camera, Upload, Loader2, Plus, Check, ImageIcon, Search } from "lucide-react";

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

  // Editable results
  const [editingIdx, setEditingIdx] = useState<number | null>(null);

  // Fallback manual entry state
  const [showFallback, setShowFallback] = useState(false);
  const [fallbackName, setFallbackName] = useState("");
  const [fallbackPortion, setFallbackPortion] = useState("");
  const [estimating, setEstimating] = useState(false);

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
    setShowFallback(false);
  };

  const startCamera = async () => {
    try {
      setMode("camera");
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
      });
      const waitForVideo = () => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        } else {
          requestAnimationFrame(waitForVideo);
        }
      };
      waitForVideo();
    } catch {
      setMode("idle");
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
        const stream = videoRef.current?.srcObject as MediaStream;
        stream?.getTracks().forEach((t) => t.stop());
      }
    }, "image/jpeg", 0.9);

    setResult(null);
    setLoggedItems(new Set());
    setShowFallback(false);
  };

  const analyzeFood = async () => {
    if (!selectedFile) return;
    setAnalyzing(true);
    setError("");
    setShowFallback(false);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      const data = await api.postForm<AnalysisResult>("/food/analyze", formData);
      setResult(data);
    } catch {
      setShowFallback(true);
    } finally {
      setAnalyzing(false);
    }
  };

  const estimateFromName = async () => {
    if (!fallbackName || !fallbackPortion) return;
    setEstimating(true);
    setError("");

    try {
      const item = await api.post<FoodItem>("/food/estimate", {
        food_name: fallbackName,
        portion: fallbackPortion,
      });
      setResult({
        foods: [item],
        image_url: null,
        total_calories: item.calories,
        total_protein: item.protein_g,
        total_fat: item.fat_g,
        total_carbs: item.carbs_g,
      });
      setShowFallback(false);
    } catch (err: any) {
      setError(err.message || "Estimation failed");
    } finally {
      setEstimating(false);
    }
  };

  const updateFoodItem = (index: number, field: keyof FoodItem, value: string | number) => {
    if (!result) return;
    const updated = [...result.foods];
    updated[index] = { ...updated[index], [field]: value };
    setResult({
      ...result,
      foods: updated,
      total_calories: updated.reduce((s, f) => s + Number(f.calories), 0),
      total_protein: updated.reduce((s, f) => s + Number(f.protein_g), 0),
      total_fat: updated.reduce((s, f) => s + Number(f.fat_g), 0),
      total_carbs: updated.reduce((s, f) => s + Number(f.carbs_g), 0),
    });
  };

  const logFoodItem = async (item: FoodItem, index: number) => {
    try {
      await api.post("/food/log", {
        meal_type: mealType,
        food_name: item.name,
        calories: Number(item.calories),
        protein_g: Number(item.protein_g),
        fat_g: Number(item.fat_g),
        carbs_g: Number(item.carbs_g),
        portion: item.portion,
        image_url: result?.image_url,
        detected_by: "ai",
      });
      setLoggedItems((prev) => new Set(prev).add(index));
      setEditingIdx(null);
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
    setShowFallback(false);
    setFallbackName("");
    setFallbackPortion("");
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
                <select
                  value={mealType}
                  onChange={(e) => setMealType(e.target.value)}
                  className="input-field !w-auto"
                >
                  <option value="breakfast">Breakfast</option>
                  <option value="lunch">Lunch</option>
                  <option value="dinner">Dinner</option>
                  <option value="snack">Snack</option>
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

            {/* Fallback: AI couldn't detect — ask user to type */}
            {showFallback && (
              <div className="glass-card p-6 animate-fade-in">
                <p className="text-sm text-[var(--text-muted)] mb-3">
                  Couldn&apos;t identify the food from the image. Tell us what it is and we&apos;ll estimate the nutrition.
                </p>
                <div className="space-y-3">
                  <input
                    className="input-field"
                    placeholder="What food is this? (e.g., samosa, biryani, pasta)"
                    value={fallbackName}
                    onChange={(e) => setFallbackName(e.target.value)}
                  />
                  <input
                    className="input-field"
                    placeholder="Portion (e.g., 2 pieces, 1 bowl, 1 large plate)"
                    value={fallbackPortion}
                    onChange={(e) => setFallbackPortion(e.target.value)}
                  />
                  <button
                    onClick={estimateFromName}
                    disabled={estimating || !fallbackName || !fallbackPortion}
                    className="btn-primary w-full flex items-center justify-center gap-2"
                  >
                    {estimating ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" /> Estimating...
                      </>
                    ) : (
                      <>
                        <Search className="w-4 h-4" /> Estimate Nutrition
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}

            {/* Results */}
            {result && (
              <div className="glass-card p-6 animate-fade-in">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="font-semibold text-[var(--accent-green)]">
                    Detected {result.foods.length} item{result.foods.length !== 1 ? "s" : ""}
                  </h2>
                  <span className="text-xs text-[var(--text-muted)]">
                    Tap to edit, + to save
                  </span>
                </div>
                <div className="space-y-3">
                  {result.foods.map((food, idx) => (
                    <div key={idx} className="p-4 rounded-xl bg-[var(--bg-secondary)]">
                      {editingIdx === idx ? (
                        <div className="space-y-2">
                          <input className="input-field text-sm" value={food.name}
                            onChange={(e) => updateFoodItem(idx, "name", e.target.value)} placeholder="Food name" />
                          <input className="input-field text-sm" value={food.portion || ""}
                            onChange={(e) => updateFoodItem(idx, "portion", e.target.value)} placeholder="Portion" />
                          <div className="grid grid-cols-4 gap-2">
                            <div>
                              <label className="text-[10px] text-[var(--text-muted)]">Cal</label>
                              <input className="input-field text-sm text-center" type="number" value={food.calories}
                                onChange={(e) => updateFoodItem(idx, "calories", parseFloat(e.target.value) || 0)} />
                            </div>
                            <div>
                              <label className="text-[10px] text-[var(--text-muted)]">Protein</label>
                              <input className="input-field text-sm text-center" type="number" value={food.protein_g}
                                onChange={(e) => updateFoodItem(idx, "protein_g", parseFloat(e.target.value) || 0)} />
                            </div>
                            <div>
                              <label className="text-[10px] text-[var(--text-muted)]">Fat</label>
                              <input className="input-field text-sm text-center" type="number" value={food.fat_g}
                                onChange={(e) => updateFoodItem(idx, "fat_g", parseFloat(e.target.value) || 0)} />
                            </div>
                            <div>
                              <label className="text-[10px] text-[var(--text-muted)]">Carbs</label>
                              <input className="input-field text-sm text-center" type="number" value={food.carbs_g}
                                onChange={(e) => updateFoodItem(idx, "carbs_g", parseFloat(e.target.value) || 0)} />
                            </div>
                          </div>
                          <div className="flex gap-2">
                            <button onClick={() => logFoodItem(food, idx)}
                              className="btn-primary flex-1 text-sm flex items-center justify-center gap-1">
                              <Check className="w-3.5 h-3.5" /> Save
                            </button>
                            <button onClick={() => setEditingIdx(null)}
                              className="btn-secondary text-sm">Cancel</button>
                          </div>
                        </div>
                      ) : (
                        <div className="flex items-center justify-between">
                          <div className="flex-1 cursor-pointer" onClick={() => !loggedItems.has(idx) && setEditingIdx(idx)}>
                            <p className="font-medium capitalize">{food.name}</p>
                            <p className="text-xs text-[var(--text-muted)] mt-1">
                              {food.portion && <span>{food.portion} · </span>}
                              P: {food.protein_g}g · F: {food.fat_g}g · C: {food.carbs_g}g
                              {!loggedItems.has(idx) && <span className="text-[var(--accent-green)] ml-1">(tap to edit)</span>}
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
                      )}
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
