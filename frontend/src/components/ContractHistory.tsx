/**
 * Contract History Component
 *
 * Displays list of all uploaded contracts with ability to view details.
 */

import { useEffect, useState } from "react";
import SummaryCard from "./SummaryCard";
import RisksCard from "./RisksCard";
import ClausesCard from "./ClausesCard";
import RecommendationsCard from "./RecommendationsCard";
import ContractFooter from "./ContractFooter";
import AnalysisStatsBar from "./AnalysisStatsBar";
import { ContractAnalysis } from "@/types/contract";
import { formatLocalDateTime } from "@/lib/date";

interface ContractSummary {
  contract_id: string;
  file_name: string;
  processing_status: string;
  created_at: string;
  file_size?: number;
  page_count?: number;
}

interface ContractHistoryProps {
  onBack: () => void;
  onViewDetails: (analysis: ContractAnalysis) => void;
}

function formatDate(value?: string): string {
  return (
    formatLocalDateTime(value, {
      month: "short",
    }) ?? "Unknown"
  );
}

function StatusBadge({ status }: { status: string }) {
  const s = status?.toLowerCase() ?? "";
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

export default function ContractHistory({
  onBack,
  onViewDetails,
}: ContractHistoryProps) {
  const [contracts, setContracts] = useState<ContractSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedContract, setSelectedContract] =
    useState<ContractAnalysis | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [loadingDetailId, setLoadingDetailId] = useState<string | null>(null);
  const [detailError, setDetailError] = useState<string | null>(null);

  useEffect(() => {
    fetchContracts();
  }, []);

  const fetchContracts = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch("http://localhost:8000/api/v1/contracts");

      if (!response.ok) {
        throw new Error("Failed to fetch contracts");
      }

      const result = await response.json();

      if (!result.success) {
        throw new Error(result.message ?? "Failed to load contracts");
      }

      setContracts(result.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load contracts");
    } finally {
      setLoading(false);
    }
  };

  const handleViewContract = async (contractId: string) => {
    try {
      setLoadingDetail(true);
      setLoadingDetailId(contractId);
      setDetailError(null);

      const response = await fetch(
        `http://localhost:8000/api/v1/contracts/${contractId}`
      );

      if (!response.ok) {
        throw new Error(
          response.status === 404 ? "Contract not found" : "Failed to fetch contract details"
        );
      }

      const result = await response.json();

      if (!result.success) {
        throw new Error(result.message ?? "Failed to load contract");
      }

      setSelectedContract(result.data);
      onViewDetails(result.data);
    } catch (err) {
      setDetailError(err instanceof Error ? err.message : "Failed to load contract details");
    } finally {
      setLoadingDetail(false);
      setLoadingDetailId(null);
    }
  };

  if (selectedContract) {
    return (
      <div>
        {/* Results Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 sm:text-3xl">
              Contract Details
            </h2>
            <p className="mt-2 text-gray-600">
              {selectedContract.file_name}
            </p>
            {selectedContract.created_at && (
              <p className="mt-1 text-sm text-gray-500">
                Analysis completed on {formatDate(selectedContract.created_at)}
              </p>
            )}
            <p className="mt-1 text-xs text-gray-400">
              Contract ID: {selectedContract.contract_id}
            </p>
          </div>
          <button
            onClick={() => setSelectedContract(null)}
            className="rounded-lg border border-gray-300 bg-white px-4 py-2 font-medium text-gray-700 transition-colors hover:bg-gray-50 sm:px-6"
          >
            ← Back to History
          </button>
        </div>

        {/* Statistics Bar */}
        <div className="mb-8">
          <AnalysisStatsBar analysis={selectedContract} />
        </div>

        {/* Results Grid */}
        <div className="space-y-8">
          <SummaryCard
            title={selectedContract.file_name}
            summary={selectedContract.summary}
            metadata={selectedContract.metadata}
          />

          <div className="grid gap-6 lg:grid-cols-2">
            <RisksCard risks={selectedContract.risks} />
            <ClausesCard clauses={selectedContract.clauses} />
          </div>

          <RecommendationsCard
            recommendations={selectedContract.recommendations}
          />

          <ContractFooter analysis={selectedContract} />
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 sm:text-3xl">
            Contract History
          </h2>
          <p className="mt-2 text-gray-600">
            View all uploaded contracts and their analyses
          </p>
        </div>
        <button
          onClick={onBack}
          className="rounded-lg border border-gray-300 bg-white px-4 py-2 font-medium text-gray-700 transition-colors hover:bg-gray-50 sm:px-6"
        >
          ← Back to Upload
        </button>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-40 animate-pulse rounded-lg bg-gray-200"
            />
          ))}
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
          <p className="text-sm font-medium text-red-800">{error}</p>
          <button
            onClick={fetchContracts}
            className="mt-2 text-sm font-medium text-red-600 hover:text-red-700"
          >
            Try Again
          </button>
        </div>
      )}

      {/* Detail Error */}
      {detailError && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 p-4">
          <p className="text-sm font-medium text-red-800">{detailError}</p>
          <button
            onClick={() => setDetailError(null)}
            className="mt-1 text-xs font-medium text-red-600 hover:text-red-700"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && contracts.length === 0 && (
        <div className="rounded-lg border border-gray-200 bg-white p-12 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-lg bg-gray-100">
            <span className="text-2xl">📄</span>
          </div>
          <h3 className="text-lg font-semibold text-gray-900">
            No contracts found
          </h3>
          <p className="mt-2 text-gray-600">
            Get started by uploading your first contract
          </p>
          <button
            onClick={onBack}
            className="mt-4 rounded-lg bg-blue-600 px-4 py-2 font-medium text-white transition-colors hover:bg-blue-700"
          >
            Upload Contract
          </button>
        </div>
      )}

      {/* Contracts Grid */}
      {!loading && !error && contracts.length > 0 && (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {contracts.map((contract) => (
            <div
              key={contract.contract_id}
              className="rounded-lg border border-gray-200 bg-white p-6 hover:shadow-md transition-shadow"
            >
              {/* File Name */}
              <h3 className="truncate font-semibold text-gray-900">
                {contract.file_name}
              </h3>

              {/* Meta Info */}
              <div className="mt-4 space-y-2 text-sm text-gray-600">
                {/* Date */}
                <div className="flex items-center gap-2">
                  <span className="text-gray-400">📅</span>
                  <span>{formatDate(contract.created_at)}</span>
                </div>

                {/* Status */}
                <div className="flex items-center gap-2">
                  <StatusBadge status={contract.processing_status} />
                </div>

                {/* File Size */}
                {contract.file_size != null && (
                  <div className="flex items-center gap-2">
                    <span className="text-gray-400">📦</span>
                    <span>
                      {(contract.file_size / 1024 / 1024).toFixed(2)} MB
                    </span>
                  </div>
                )}

                {/* Page Count */}
                {contract.page_count != null && (
                  <div className="flex items-center gap-2">
                    <span className="text-gray-400">📃</span>
                    <span>{contract.page_count} pages</span>
                  </div>
                )}
              </div>

              {/* View Button */}
              <button
                onClick={() => handleViewContract(contract.contract_id)}
                disabled={loadingDetail}
                className="mt-4 w-full rounded-lg bg-blue-600 py-2 font-medium text-white transition-colors hover:bg-blue-700 disabled:opacity-60"
              >
                {loadingDetail && loadingDetailId === contract.contract_id
                  ? "Loading..."
                  : "View Details →"}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

