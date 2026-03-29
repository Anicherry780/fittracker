import Link from "next/link";
import { Flame, Camera, Dumbbell, UtensilsCrossed, ArrowRight, ShieldCheck } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-[var(--accent-green)]/5 via-transparent to-[var(--accent-emerald)]/5" />
        <div className="max-w-6xl mx-auto px-6 pt-20 pb-28 relative">
          <div className="flex flex-col items-center text-center gap-6">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[var(--accent-green)] to-[var(--accent-emerald)] flex items-center justify-center mb-2">
              <Flame className="w-8 h-8 text-[var(--bg-primary)]" />
            </div>
            <h1 className="text-5xl md:text-7xl font-bold tracking-tight">
              <span className="gradient-text">FitTracker</span>
            </h1>
            <p className="text-xl text-[var(--text-secondary)] max-w-2xl">
              AI-powered fitness & nutrition tracker. Snap your food, track your workout,
              and let AI handle the calorie math.
            </p>
            <div className="flex gap-4 mt-4">
              <Link href="/register" className="btn-primary flex items-center gap-2 text-lg !px-8 !py-3">
                Get Started <ArrowRight className="w-5 h-5" />
              </Link>
              <Link href="/login" className="btn-secondary flex items-center gap-2 text-lg !px-8 !py-3">
                Login
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-6 pb-20">
        <div className="grid md:grid-cols-3 gap-6">
          {[
            {
              icon: Camera,
              title: "AI Food Scanner",
              desc: "Snap a photo of any meal. Our AI identifies every item and calculates calories, protein, fat, and carbs instantly.",
              color: "var(--accent-green)",
            },
            {
              icon: Dumbbell,
              title: "Workout Tracker",
              desc: "Log 60+ exercises with auto-calculated calorie burn using scientifically-backed MET values.",
              color: "var(--accent-lime)",
            },
            {
              icon: UtensilsCrossed,
              title: "Smart Calorie Balance",
              desc: "See exactly how many calories you can still eat today based on your TDEE and exercise.",
              color: "var(--accent-emerald)",
            },
          ].map((feature) => {
            const Icon = feature.icon;
            return (
              <div
                key={feature.title}
                className="glass-card p-8 hover:scale-[1.02] transition-transform animate-fade-in"
              >
                <div
                  className="w-12 h-12 rounded-xl flex items-center justify-center mb-4"
                  style={{ background: `${feature.color}15` }}
                >
                  <Icon className="w-6 h-6" style={{ color: feature.color }} />
                </div>
                <h3 className="text-lg font-bold mb-2">{feature.title}</h3>
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{feature.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Disclaimer footer */}
      <footer className="border-t border-[var(--border-color)] py-8 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-sm text-[var(--text-muted)]">
            <Flame className="w-4 h-4 text-[var(--accent-green)]" />
            <span>FitTracker &copy; {new Date().getFullYear()}</span>
          </div>
          <div className="flex items-start gap-2 max-w-xl">
            <ShieldCheck className="w-4 h-4 text-[var(--warning)] mt-0.5 shrink-0" />
            <p className="text-xs text-[var(--text-muted)] leading-relaxed">
              <strong className="text-[var(--warning)]">Disclaimer:</strong> FitTracker provides
              AI-estimated nutritional information for informational purposes only. Calorie and
              macro values are approximations and should not be used as medical or dietary advice.
              Always consult a qualified healthcare professional or registered dietitian before
              making changes to your diet or exercise routine. We are not liable for any health
              decisions made based on this tool.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
