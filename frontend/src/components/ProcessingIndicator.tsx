"use client";

/**
 * Processing Indicator Component
 *
 * Shows upload and processing status with progress bar.
 */

import { ProcessingState } from "@/types/contract";

interface ProcessingIndicatorProps {
  state: ProcessingState;
}

export default function ProcessingIndicator({
  state,
}: ProcessingIndicatorProps) {
  if (state.status === "idle") return null;

  const isProcessing = state.status === "processing";
  const isCompleted = state.status === "completed";
  const isError = state.status === "error";

  return (
    <div className={`rounded-lg border p-4 sm:p-6 ${
      isError
        ? "border-red-200 bg-red-50"
        : isCompleted
          ? "border-green-200 bg-green-50"
          : "border-blue-200 bg-blue-50"
    }`}>
      <div className="flex items-center gap-4">
        {/* Status Icon */}
        <div className="flex-shrink-0">
          {isProcessing && (
            <div className="flex h-10 w-10 items-center justify-center">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-blue-600 border-t-blue-200" />
            </div>
          )}
          {isCompleted && (
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-green-200">
              <svg
                className="h-6 w-6 text-green-600"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
          )}
          {isError && (
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-red-200">
              <svg
                className="h-6 w-6 text-red-600"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
          )}
        </div>

        {/* Message and Progress */}
        <div className="flex-1">
          <p className={`font-semibold ${
            isError
              ? "text-red-900"
              : isCompleted
                ? "text-green-900"
                : "text-blue-900"
          }`}>
            {state.message}
          </p>
          {isError && state.error && (
            <p className="mt-1 text-sm text-red-700">{state.error}</p>
          )}

          {/* Progress Bar */}
          {(isProcessing || state.status === "uploading") && (
            <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-blue-200">
              <div
                className="h-full bg-blue-600 transition-all duration-300"
                style={{ width: `${state.progress}%` }}
              />
            </div>
          )}

          {isProcessing && (
            <p className="mt-2 text-xs text-blue-700">
              {state.progress}% complete
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
