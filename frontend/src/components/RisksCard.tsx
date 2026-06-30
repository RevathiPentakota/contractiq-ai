/**
 * Risks Card Component
 *
 * Displays identified risks with severity levels and recommendations.
 */

import Card from "./Card";
import Badge from "./Badge";
import { Risk } from "@/types/contract";

interface RisksCardProps {
  risks: Risk[];
}

const SEVERITY_ORDER: Record<string, number> = {
  critical: 0,
  high: 1,
  medium: 2,
  low: 3,
};

function getSeverityStyles(severity: string): {
  card: string;
  badge: string;
  dot: string;
} {
  switch (severity.toLowerCase()) {
    case "critical":
      return {
        card: "border-l-4 border-red-600 bg-red-50",
        badge: "bg-red-100 text-red-800",
        dot: "bg-red-600",
      };
    case "high":
      return {
        card: "border-l-4 border-orange-500 bg-orange-50",
        badge: "bg-orange-100 text-orange-800",
        dot: "bg-orange-500",
      };
    case "medium":
      return {
        card: "border-l-4 border-amber-400 bg-amber-50",
        badge: "bg-amber-100 text-amber-800",
        dot: "bg-amber-400",
      };
    case "low":
      return {
        card: "border-l-4 border-green-500 bg-green-50",
        badge: "bg-green-100 text-green-800",
        dot: "bg-green-500",
      };
    default:
      return {
        card: "border-l-4 border-gray-300 bg-gray-50",
        badge: "bg-gray-100 text-gray-700",
        dot: "bg-gray-400",
      };
  }
}

export default function RisksCard({ risks }: RisksCardProps) {
  const sorted = [...risks].sort((a, b) => {
    const aOrder = SEVERITY_ORDER[a.severity?.toLowerCase() ?? ""] ?? 4;
    const bOrder = SEVERITY_ORDER[b.severity?.toLowerCase() ?? ""] ?? 4;
    return aOrder - bOrder;
  });

  const criticalCount = risks.filter(
    (r) => r.severity?.toLowerCase() === "critical"
  ).length;
  const highCount = risks.filter(
    (r) => r.severity?.toLowerCase() === "high"
  ).length;

  return (
    <Card
      title="Identified Risks"
      description={`${risks.length} risks found (${criticalCount} critical, ${highCount} high)`}
      icon={
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-red-100">
          <svg
            className="h-5 w-5 text-red-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"
            />
          </svg>
        </div>
      }
    >
      <div className="space-y-3">
        {sorted.length === 0 ? (
          <div className="rounded-lg border-2 border-dashed border-gray-200 p-6 text-center">
            <p className="text-sm text-gray-500">No risks found</p>
          </div>
        ) : (
          sorted.map((risk, index) => {
            const styles = getSeverityStyles(risk.severity ?? "");
            return (
              <div
                key={index}
                className={`rounded-lg p-4 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md ${styles.card}`}
              >
                {/* Header row: severity badge + category */}
                <div className="flex items-start justify-between gap-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge className={styles.badge}>
                      {risk.severity
                        ? risk.severity.charAt(0).toUpperCase() +
                          risk.severity.slice(1).toLowerCase()
                        : "—"}
                    </Badge>
                    {risk.category && (
                      <span className="text-xs font-medium text-gray-500">
                        {risk.category}
                      </span>
                    )}
                  </div>
                </div>

                {/* Title */}
                <p className="mt-2 text-sm font-semibold text-gray-900">
                  {risk.title}
                </p>

                {/* Description */}
                <p className="mt-1.5 text-sm leading-[1.7] text-gray-700">
                  {risk.description}
                </p>

                {/* Footer: reference + recommendation always pinned at bottom */}
                {(risk.clause_reference || risk.recommendation) && (
                  <div className="mt-3 space-y-1.5 border-t border-black/5 pt-3">
                    {risk.clause_reference && (
                      <p className="text-xs text-gray-500">
                        <span className="font-medium text-gray-600">§ Ref:</span>{" "}
                        {risk.clause_reference}
                      </p>
                    )}
                    {risk.recommendation && (
                      <p className="text-xs leading-[1.6] text-gray-700">
                        <span className="font-medium text-blue-700">✓ Recommendation:</span>{" "}
                        {risk.recommendation}
                      </p>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </Card>
  );
}

