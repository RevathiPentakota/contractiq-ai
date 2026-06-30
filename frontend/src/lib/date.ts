function normalizeTimestamp(value: string): string {
  const trimmed = value.trim();
  const withIsoSeparator = trimmed.replace(" ", "T");
  const hasTimezone = /(?:Z|[+-]\d{2}:?\d{2})$/i.test(withIsoSeparator);
  const withMilliseconds = withIsoSeparator.replace(
    /\.(\d{3})\d+/,
    ".$1"
  );

  return hasTimezone ? withMilliseconds : `${withMilliseconds}Z`;
}

export function parseUtcTimestamp(value?: string): Date | null {
  if (!value) return null;

  const date = new Date(normalizeTimestamp(value));
  return Number.isNaN(date.getTime()) ? null : date;
}

export function formatLocalDateTime(
  value?: string,
  options?: Intl.DateTimeFormatOptions
): string | null {
  const date = parseUtcTimestamp(value);
  if (!date) return null;

  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    ...options,
  });
}
