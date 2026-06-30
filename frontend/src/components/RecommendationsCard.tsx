/**
 * Recommendations Card Component
 *
 * Displays actionable recommendations for contract improvements.
 */

import Card from "./Card";
import Badge from "./Badge";
import { Recommendation } from "@/types/contract";

interface RecommendationsCardProps {
  recommendations: Recommendation[];
}

const PRIORITY_ORDER: Record<string, number> = {
  high: 0,
  medium: 1,
  low: 2,
};

function getPriorityStyles(priority: string): {
  card: string;
  badge: string;
  indicator: string;
} {
  switch (priority.toLowerCase()) {
    case "high":
      return {
        card: "border-l-4 border-red-500 bg-red-50",
        badge: "bg-red-100 text-red-800",
        indicator: "bg-red-500",
      };
    case "medium":
      return {
        card: "border-l-4 border-amber-400 bg-amber-50",
        badge: "bg-amber-100 text-amber-800",
        indicator: "bg-amber-400",
      };
    case "low":
      return {
        card: "border-l-4 border-green-500 bg-green-50",
        badge: "bg-green-100 text-green-800",
        indicator: "bg-green-500",
      };
    default:
      return {
        card: "border-l-4 border-gray-300 bg-gray-50",
        badge: "bg-gray-100 text-gray-700",
        indicator: "bg-gray-400",
      };
  }
}

export default function RecommendationsCard({
  recommendations,
}: RecommendationsCardProps) {
  const sorted = [...recommendations].sort((a, b) => {
    const aOrder = PRIORITY_ORDER[a.priority?.toLowerCase() ?? ""] ?? 3;
    const bOrder = PRIORITY_ORDER[b.priority?.toLowerCase() ?? ""] ?? 3;
    return aOrder - bOrder;
  });

  const highCount = recommendations.filter(
    (r) => r.priority?.toLowerCase() === "high"
  ).length;

  return (
    <Card
      title="Recommendations"
      description={`${recommendations.length} recommendations (${highCount} high priority)`}
      contentClassName="px-6 py-3 sm:px-8 sm:py-4"
      icon={
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-green-100">
          <svg
            className="h-5 w-5 text-green-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
      }
    >
      <div className="space-y-2">
        {sorted.length === 0 ? (
          <div className="rounded-lg border-2 border-dashed border-gray-200 p-6 text-center">
            <p className="text-sm text-gray-500">No recommendations found</p>
          </div>
        ) : (
          sorted.map((rec, index) => {
            const styles = getPriorityStyles(rec.priority ?? "");
            return (
              <div
                key={index}
                className={`rounded-lg px-4 py-2.5 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md ${styles.card}`}
              >
                {/* Header: title + priority badge top-right */}
                <div className="flex items-start justify-between gap-3">
                  <p className="text-sm font-semibold leading-5 text-gray-900">
                    {rec.title || "—"}
                  </p>
                  <Badge className={`shrink-0 ${styles.badge}`}>
                    {rec.priority
                      ? rec.priority.charAt(0).toUpperCase() +
                        rec.priority.slice(1).toLowerCase()
                      : "—"}{" "}
                    Priority
                  </Badge>
                </div>

                {/* Category / description */}
                {rec.description && (
                  <p className="mt-1 text-sm leading-5 text-gray-600">
                    {rec.description}
                  </p>
                )}

                {/* Rationale */}
                {rec.reason && (
                  <p className="mt-1.5 text-xs italic leading-5 text-gray-500">
                    {rec.reason}
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

