/**
 * Clauses Card Component
 *
 * Displays extracted contract clauses organized by importance.
 */

import Card from "./Card";
import { Clause } from "@/types/contract";

interface ClausesCardProps {
  clauses: Clause[];
}

const IMPORTANCE_ORDER: Record<string, number> = {
  high: 0,
  medium: 1,
  low: 2,
};

function getImportanceStyles(importance: string): {
  card: string;
  badge: string;
} {
  switch (importance.toLowerCase()) {
    case "high":
      return {
        card: "border-l-4 border-blue-500 bg-blue-50",
        badge: "bg-blue-100 text-blue-800",
      };
    case "medium":
      return {
        card: "border-l-4 border-amber-400 bg-amber-50",
        badge: "bg-amber-100 text-amber-800",
      };
    case "low":
      return {
        card: "border-l-4 border-gray-300 bg-white",
        badge: "bg-gray-100 text-gray-700",
      };
    default:
      return {
        card: "border-l-4 border-gray-200 bg-gray-50",
        badge: "bg-gray-100 text-gray-700",
      };
  }
}

export default function ClausesCard({ clauses }: ClausesCardProps) {
  const sorted = [...clauses].sort((a, b) => {
    const aOrder = IMPORTANCE_ORDER[a.importance?.toLowerCase() ?? ""] ?? 3;
    const bOrder = IMPORTANCE_ORDER[b.importance?.toLowerCase() ?? ""] ?? 3;
    return aOrder - bOrder;
  });

  const highCount = clauses.filter(
    (c) => c.importance?.toLowerCase() === "high"
  ).length;

  return (
    <Card
      title="Key Clauses"
      description={`${clauses.length} clauses identified (${highCount} high importance)`}
      icon={
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-100">
          <svg
            className="h-5 w-5 text-blue-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
        </div>
      }
    >
      <div className="space-y-3">
        {sorted.length === 0 ? (
          <div className="rounded-lg border-2 border-dashed border-gray-200 p-6 text-center">
            <p className="text-sm text-gray-500">No clauses found</p>
          </div>
        ) : (
          sorted.map((clause, index) => {
            const styles = getImportanceStyles(clause.importance ?? "");
            return (
              <div
                key={index}
                className={`rounded-lg p-4 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md ${styles.card}`}
              >
                {/* Header: importance badge + category pill */}
                <div className="flex flex-wrap items-center gap-2">
                  <span
                    className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-semibold ${styles.badge}`}
                  >
                    {clause.importance
                      ? clause.importance.charAt(0).toUpperCase() +
                        clause.importance.slice(1).toLowerCase()
                      : "—"}
                  </span>
                  {clause.category && (
                    <span className="rounded-full bg-gray-200 px-2 py-0.5 text-xs font-medium text-gray-700">
                      {clause.category}
                    </span>
                  )}
                </div>

                {/* Title */}
                <h3 className="mt-2 text-sm font-semibold text-gray-900">
                  {clause.title}
                </h3>

                {/* Description */}
                <p className="mt-1.5 text-sm leading-[1.7] text-gray-700">
                  {clause.description}
                </p>

                {/* Clause reference */}
                {clause.clause_reference && (
                  <p className="mt-2.5 text-xs text-gray-500">
                    <span className="font-medium text-gray-600">§ Location:</span>{" "}
                    {clause.clause_reference}
                  </p>
                )}
              </div>
            );
          })
        )}
      </div>
    </Card>
  );
}


