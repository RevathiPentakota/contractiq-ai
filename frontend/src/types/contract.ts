/**
 * Contract Analysis Type Definitions
 *
 * These types represent the structure of contract analysis results
 * from the ContractIQ AI backend.
 */

export interface Risk {
  category: string;
  severity: string;
  title: string;
  description: string;
  clause_reference?: string;
  recommendation?: string;
}

export interface Clause {
  title: string;
  category: string;
  clause_reference?: string;
  description: string;
  importance: string;
}

export interface Recommendation {
  priority: string;
  title: string;
  description: string;
  reason: string;
}

export interface ContractAnalysis {
  contract_id: string;
  file_name: string;
  summary: string;
  risks: Risk[];
  clauses: Clause[];
  recommendations: Recommendation[];
  metadata: {
    file_size?: number;
    word_count?: number;
    page_count?: number;
    format?: string;
  };
  processing_status?: string;
  created_at?: string;
}

export interface ProcessingState {
  status: "idle" | "uploading" | "processing" | "completed" | "error";
  progress: number;
  message: string;
  error?: string;
}
