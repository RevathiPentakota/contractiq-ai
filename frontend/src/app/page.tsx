"use client";

/**
 * Main Dashboard Page
 *
 * Complete contract analysis interface combining all components.
 * Uses FastAPI backend for contract analysis.
 */

import { useState } from "react";
import Header from "@/components/Header";
import UploadSection from "@/components/UploadSection";
import ProcessingIndicator from "@/components/ProcessingIndicator";
import SummaryCard from "@/components/SummaryCard";
import RisksCard from "@/components/RisksCard";
import ClausesCard from "@/components/ClausesCard";
import RecommendationsCard from "@/components/RecommendationsCard";
import ContractHistory from "@/components/ContractHistory";
import ContractFooter from "@/components/ContractFooter";
import AnalysisStatsBar from "@/components/AnalysisStatsBar";

import { ContractAnalysis, ProcessingState } from "@/types/contract";

export default function Dashboard() {
  const [currentPage, setCurrentPage] = useState<"dashboard" | "history">(
    "dashboard"
  );
  const [analysis, setAnalysis] = useState<ContractAnalysis | null>(null);
  const [processingState, setProcessingState] = useState<ProcessingState>({
    status: "idle",
    message: "",
    progress: 0,
  });
  const [showResults, setShowResults] = useState(false);

const handleUpload = async (file: File) => {
  try {
    setShowResults(false);

    setProcessingState({
      status: "uploading",
      message: "Uploading contract...",
      progress: 10,
    });

    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(
      "http://localhost:8000/api/v1/contracts/upload",
      {
        method: "POST",
        body: formData,
      }
    );

    if (!response.ok) {
      throw new Error("Upload failed");
    }

    setProcessingState({
      status: "completed",
      message: "Analysis completed",
      progress: 100,
    });

    const result = await response.json();

    if (!result.success) {
      throw new Error(result.message ?? "Processing failed");
    }

    setAnalysis(result.data);
    setShowResults(true);
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Contract analysis failed.";
    alert(message);
  }
};

  const handleReset = () => {
    setAnalysis(null);
    setProcessingState({
      status: "idle",
      message: "",
      progress: 0,
    });
    setShowResults(false);
  };

  const handleNavigateToDashboard = () => {
    setCurrentPage("dashboard");
    handleReset();
  };

  const handleNavigateToHistory = () => {
    setCurrentPage("history");
  };

  const handleViewDetailsFromHistory = (contractAnalysis: ContractAnalysis) => {
    setAnalysis(contractAnalysis);
    setShowResults(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <Header
        onNavigateToDashboard={handleNavigateToDashboard}
        onNavigateToHistory={handleNavigateToHistory}
        currentPage={currentPage}
      />

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 sm:py-12 lg:px-8">
        {/* History View */}
        {currentPage === "history" && (
          <ContractHistory
            onBack={handleNavigateToDashboard}
            onViewDetails={handleViewDetailsFromHistory}
          />
        )}

        {/* Dashboard View */}
        {currentPage === "dashboard" && (
          <>
            {/* Upload Section */}
            {!showResults && (
              <div className="mb-8">
                <div className="mb-6">
                  <h2 className="text-2xl font-bold text-gray-900 sm:text-3xl">
                    Upload Your Contract
                  </h2>
                  <p className="mt-2 text-gray-600">
                    Drop your PDF contract and let AI analyze it instantly
                  </p>
                </div>
                <UploadSection onUpload={handleUpload} />
              </div>
            )}

            {/* Processing Indicator */}
            {processingState.status !== "idle" && (
              <div className="mb-8">
                <ProcessingIndicator state={processingState} />
              </div>
            )}

            {/* Results Section */}
            {showResults && analysis && (
              <>
                {/* Results Header */}
                <div className="mb-8 flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 sm:text-3xl">
                      Analysis Results
                    </h2>
                    <p className="mt-2 text-gray-600">
                      Complete contract analysis for {analysis.file_name}
                    </p>
                  </div>
                  <button
                    onClick={handleReset}
                    className="rounded-lg border border-gray-300 bg-white px-4 py-2 font-medium text-gray-700 transition-colors hover:bg-gray-50 sm:px-6"
                  >
                    ← Upload New Contract
                  </button>
                </div>

                {/* Statistics Bar */}
                <div className="mb-8">
                  <AnalysisStatsBar analysis={analysis} />
                </div>

                {/* Results Grid */}
                <div className="space-y-8">
                  {/* Summary */}
                  <SummaryCard
                    title={analysis.file_name}
                    summary={analysis.summary}
                    metadata={analysis.metadata}
                  />

                  {/* Risks & Clauses Row */}
                  <div className="grid gap-6 lg:grid-cols-2">
                    <RisksCard risks={analysis.risks} />
                    <ClausesCard clauses={analysis.clauses} />
                  </div>

                  {/* Recommendations */}
                  <RecommendationsCard
                    recommendations={analysis.recommendations}
                  />

                  {/* Footer */}
                  <ContractFooter analysis={analysis} />
                </div>
              </>
            )}

            {/* Empty State */}
            {!showResults && processingState.status === "idle" && !analysis && (
              <div className="rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
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
                <p className="mt-4 text-gray-900">
                  No contract uploaded yet
                </p>
                <p className="mt-1 text-sm text-gray-600">
                  Start by uploading your first contract above
                </p>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}