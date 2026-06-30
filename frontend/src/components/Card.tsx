/**
 * Card Component
 *
 * Reusable card wrapper with consistent styling.
 */

interface CardProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  contentClassName?: string;
}

export default function Card({
  title,
  description,
  icon,
  children,
  className = "",
  contentClassName = "px-6 py-4 sm:px-8 sm:py-6",
}: CardProps) {
  return (
    <div className={`rounded-lg border border-gray-200 bg-white shadow-sm ${className}`}>
      {/* Header */}
      <div className="border-b border-gray-100 px-6 py-4 sm:px-8">
        <div className="flex items-start gap-4">
          {icon && <div className="flex-shrink-0">{icon}</div>}
          <div className="flex-1">
            <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
            {description && (
              <p className="mt-1 text-sm text-gray-600">{description}</p>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className={contentClassName}>{children}</div>
    </div>
  );
}
