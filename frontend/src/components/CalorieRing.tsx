"use client";

interface CalorieRingProps {
  consumed: number;
  target: number;
  burned: number;
}

export default function CalorieRing({ consumed, target, burned }: CalorieRingProps) {
  const totalBudget = target + burned;
  const remaining = Math.max(0, totalBudget - consumed);
  const percentage = Math.min((consumed / totalBudget) * 100, 100);

  // SVG circle
  const size = 200;
  const strokeWidth = 12;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;

  // Color based on percentage
  const getColor = () => {
    if (percentage > 100) return "var(--danger)";
    if (percentage > 85) return "var(--warning)";
    return "var(--accent-green)";
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative calorie-ring">
        <svg width={size} height={size} className="transform -rotate-90">
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="var(--bg-card)"
            strokeWidth={strokeWidth}
          />
          {/* Progress circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={getColor()}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-bold" style={{ color: getColor() }}>
            {Math.round(remaining)}
          </span>
          <span className="text-xs text-[var(--text-muted)] mt-1">kcal remaining</span>
        </div>
      </div>

      {/* Stats row */}
      <div className="flex gap-6 text-center">
        <div>
          <p className="text-lg font-semibold text-[var(--accent-green)]">{Math.round(consumed)}</p>
          <p className="text-xs text-[var(--text-muted)]">Eaten</p>
        </div>
        <div className="w-px bg-[var(--border-color)]" />
        <div>
          <p className="text-lg font-semibold text-[var(--accent-lime)]">{Math.round(burned)}</p>
          <p className="text-xs text-[var(--text-muted)]">Burned</p>
        </div>
        <div className="w-px bg-[var(--border-color)]" />
        <div>
          <p className="text-lg font-semibold text-[var(--text-secondary)]">{Math.round(target)}</p>
          <p className="text-xs text-[var(--text-muted)]">Target</p>
        </div>
      </div>
    </div>
  );
}
