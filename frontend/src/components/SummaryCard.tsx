/**
 * Summary Card Component
 *
 * Displays the executive summary of the contract analysis.
 * Uses react-markdown for proper rendering of headings, bold, and lists.
 */

"use client";

import ReactMarkdown from "react-markdown";
import Card from "./Card";

interface SummaryCardProps {
  title: string;
  summary: string;
  metadata: {
    file_size?: number;
    word_count?: number;
    page_count?: number;
    format?: string;
  };
}

function formatFileSize(bytes?: number): string {
  if (!bytes) return "—";
  if (bytes >= 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
  if (bytes >= 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${bytes} B`;
}

export default function SummaryCard({ title, summary, metadata }: SummaryCardProps) {
  return (
    <Card
      title="Executive Summary"
      description={title}
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
      <div className="space-y-4">
        {/* Summary Text — rendered as markdown */}
        <div className="max-w-5xl">
          {summary ? (
            <ReactMarkdown
              components={{
                h1: ({ children }) => (
                  <h1 className="mb-2 mt-3 text-xl font-bold text-gray-900 first:mt-0">
                    {children}
                  </h1>
                ),
                h2: ({ children }) => (
                  <h2 className="mb-1.5 mt-2.5 text-lg font-semibold text-gray-900 first:mt-0">
                    {children}
                  </h2>
                ),
                h3: ({ children }) => (
                  <h3 className="mb-1.5 mt-2 text-base font-semibold text-gray-800 first:mt-0">
                    {children}
                  </h3>
                ),
                p: ({ children }) => (
                  <p className="mb-3 text-base leading-7 text-gray-700 last:mb-0">
                    {children}
                  </p>
                ),
                strong: ({ children }) => (
                  <strong className="font-semibold text-gray-900">{children}</strong>
                ),
                em: ({ children }) => (
                  <em className="italic text-gray-700">{children}</em>
                ),
                ul: ({ children }) => (
                  <ul className="mb-3 ml-4 list-disc space-y-1 text-base text-gray-700">
                    {children}
                  </ul>
                ),
                ol: ({ children }) => (
                  <ol className="mb-3 ml-4 list-decimal space-y-1 text-base text-gray-700">
                    {children}
                  </ol>
                ),
                li: ({ children }) => (
                  <li className="leading-7">{children}</li>
                ),
              }}
            >
              {summary}
            </ReactMarkdown>
          ) : (
            <p className="text-sm text-gray-500">No summary available.</p>
          )}
        </div>

        {/* Metadata Grid */}
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div className="rounded-lg border border-gray-100 bg-gray-50 p-3">
            <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
              Format
            </p>
            <p className="mt-1 text-sm font-semibold text-gray-900">
              {metadata.format?.toUpperCase() || "—"}
            </p>
          </div>
          <div className="rounded-lg border border-gray-100 bg-gray-50 p-3">
            <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
              Pages
            </p>
            <p className="mt-1 text-sm font-semibold text-gray-900">
              {metadata.page_count ?? "—"}
            </p>
          </div>
          <div className="rounded-lg border border-gray-100 bg-gray-50 p-3">
            <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
              Words
            </p>
            <p className="mt-1 text-sm font-semibold text-gray-900">
              {metadata.word_count != null
                ? metadata.word_count.toLocaleString()
                : "—"}
            </p>
          </div>
          <div className="rounded-lg border border-gray-100 bg-gray-50 p-3">
            <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
              Size
            </p>
            <p className="mt-1 text-sm font-semibold text-gray-900">
              {formatFileSize(metadata.file_size)}
            </p>
          </div>
        </div>
      </div>
    </Card>
  );
}

