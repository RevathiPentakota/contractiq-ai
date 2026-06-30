/**
 * ContractFooter Component
 *
 * Displays analysis metadata: date, contract ID (shortened + copy),
 * file size, page count, and processing status.
 */

"use client";

import { useState } from "react";
import { ContractAnalysis } from "@/types/contract";
import { formatLocalDateTime } from "@/lib/date";

interface ContractFooterProps {
  analysis: ContractAnalysis;
}

function shortenId(id: string): string {
  if (id.length <= 14) return id;
  return `${id.slice(0, 8)}...${id.slice(-6)}`;
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

export default function ContractFooter({ analysis }: ContractFooterProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(analysis.contract_id);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard API not available
    }
  };

  const formattedDate = formatLocalDateTime(analysis.created_at);

  return (
    <div className="rounded-lg border border-gray-200 bg-white px-6 py-6 sm:px-8">
      <div className="grid gap-6 sm:grid-cols-3">

        {/* Analysis Date */}
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-gray-400">
            Analysis Date
          </p>
          <p className="mt-2 text-sm font-medium text-gray-800">
            {formattedDate ?? (
              <span className="text-gray-400 italic">Not available</span>
            )}
          </p>
        </div>

        {/* Contract ID */}
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-gray-400">
            Contract ID
          </p>
          <div className="mt-2 flex items-center gap-2">
            <p className="font-mono text-sm text-gray-700" title={analysis.contract_id}>
              {shortenId(analysis.contract_id)}
            </p>
            <button
              onClick={handleCopy}
              title="Copy Contract ID"
              className="rounded p-0.5 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
            >
              {copied ? (
                <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                  />
                </svg>
              )}
            </button>
          </div>
        </div>

        {/* Status */}
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-gray-400">
            Status
          </p>
          <div className="mt-2">
            <StatusBadge status={analysis.processing_status} />
          </div>
        </div>
      </div>
    </div>
  );
}
