"use client";

import { Beef, Droplets, Wheat } from "lucide-react";

interface MacroCardsProps {
  protein: number;
  fat: number;
  carbs: number;
}

export default function MacroCards({ protein, fat, carbs }: MacroCardsProps) {
  const macros = [
    {
      label: "Protein",
      value: protein,
      unit: "g",
      icon: Beef,
      color: "#3b82f6",
      bg: "rgba(59, 130, 246, 0.1)",
    },
    {
      label: "Fat",
      value: fat,
      unit: "g",
      icon: Droplets,
      color: "#f59e0b",
      bg: "rgba(245, 158, 11, 0.1)",
    },
    {
      label: "Carbs",
      value: carbs,
      unit: "g",
      icon: Wheat,
      color: "#a3e635",
      bg: "rgba(163, 230, 53, 0.1)",
    },
  ];

  return (
    <div className="grid grid-cols-3 gap-3">
      {macros.map((macro) => {
        const Icon = macro.icon;
        return (
          <div
            key={macro.label}
            className="glass-card p-4 flex flex-col items-center gap-2 hover:scale-105 transition-transform"
          >
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ background: macro.bg }}
            >
              <Icon className="w-5 h-5" style={{ color: macro.color }} />
            </div>
            <p className="text-xl font-bold" style={{ color: macro.color }}>
              {Math.round(macro.value)}
              <span className="text-xs text-[var(--text-muted)] ml-0.5">{macro.unit}</span>
            </p>
            <p className="text-xs text-[var(--text-muted)]">{macro.label}</p>
          </div>
        );
      })}
    </div>
  );
}
