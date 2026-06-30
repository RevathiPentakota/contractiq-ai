/**
 * Analysis Statistics Bar
 *
 * Displays key metrics from the contract analysis:
 * Pages, Risks, Clauses, Recommendations, Status.
 *
 * Responsive: 5 columns (desktop) → 2 columns (tablet) → 1 column (mobile)
 */

"use client";

import { ContractAnalysis } from "@/types/contract";

interface AnalysisStatsBarProps {
  analysis: ContractAnalysis;
}

function StatusBadge({ status }: { status?: string }) {
  if (!status) return null;
  const s = status.toLowerCase();
  if (s.includes("completed")) {
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-semibold text-green-800">
        ✓ Completed
      </span>
    );
  }
  if (s.includes("fail") || s.includes("error")) {
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-semibold text-red-800">
        ✕ Failed
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-yellow-100 px-2.5 py-0.5 text-xs font-semibold text-yellow-800">
      ⏳ Processing
    </span>
  );
}

export default function AnalysisStatsBar({ analysis }: AnalysisStatsBarProps) {
  const stats = [
    { icon: "📄", label: "Pages", value: analysis.metadata?.page_count ?? "—" },
    { icon: "⚠", label: "Risks", value: analysis.risks?.length ?? 0 },
    { icon: "📑", label: "Clauses", value: analysis.clauses?.length ?? 0 },
    { icon: "💡", label: "Recommendations", value: analysis.recommendations?.length ?? 0 },
  ];

  return (
    <div className="rounded-lg border border-gray-200 bg-white px-4 py-4 sm:px-6 sm:py-5">
      {/* 5 columns desktop, 2 columns tablet, 1 column mobile */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-2 md:grid-cols-5 lg:grid-cols-5">
        {/* Stats Cards */}
        {stats.map((stat, idx) => (
          <div key={idx} className="rounded-md border border-gray-100 bg-gray-50 p-3 text-center">
            <p className="text-lg">{stat.icon}</p>
            <p className="mt-1 text-xs font-medium uppercase tracking-wide text-gray-500">
              {stat.label}
            </p>
            <p className="mt-1 text-lg font-bold text-gray-900">{stat.value}</p>
          </div>
        ))}

        {/* Status Card — spans 1 or 2 columns depending on screen */}
        <div className="col-span-2 rounded-md border border-gray-100 bg-gray-50 p-3 sm:col-span-2 md:col-span-1">
          <p className="text-center text-xs font-medium uppercase tracking-wide text-gray-500">
            Status
          </p>
          <div className="mt-2 flex justify-center">
            <StatusBadge status={analysis.processing_status} />
          </div>
        </div>
      </div>
    </div>
  );
}
