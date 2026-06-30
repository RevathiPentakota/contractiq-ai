/**
 * Mock Data Generator for Contract Analysis
 *
 * Provides realistic sample data for UI development without backend connection.
 */

import { ContractAnalysis, ProcessingState } from "@/types/contract";

export function generateMockContractAnalysis(): ContractAnalysis {
  return {
    contract_id: "contract-20240629-001",
    file_name: "service-agreement-2024.pdf",
    summary:
      "This is a comprehensive Software as a Service (SaaS) agreement between Acme Corp and TechVendor Inc. The contract outlines the provision of cloud-based project management tools with a 36-month initial term. Key terms include monthly pricing of $5,000, automatic renewal provisions, and detailed service level agreements guaranteeing 99.5% uptime. The agreement covers data security, intellectual property rights, and includes standard limitation of liability clauses.",
    risks: [
      {
        category: "Payment & Billing",
        severity: "high",
        title: "Auto-Renewal Without Sufficient Notice",
        description:
          "Contract automatically renews unless cancelled 60 days before expiration. No explicit confirmation required.",
        clause_reference: "Section 3.2",
        recommendation:
          "Set calendar reminders for renewal dates or negotiate explicit opt-in requirement.",
      },
      {
        category: "Liability",
        severity: "high",
        title: "Unlimited Indemnification Obligation",
        description:
          "Your company must indemnify vendor for third-party IP claims without cap or exclusion.",
        clause_reference: "Section 8.1",
        recommendation:
          "Negotiate cap on indemnification obligations equal to annual contract value.",
      },
      {
        category: "Data Protection",
        severity: "medium",
        title: "Limited Data Breach Notification",
        description:
          "Vendor has 30 days to notify of data breach, which may be insufficient for regulatory compliance.",
        clause_reference: "Section 9.3",
        recommendation:
          "Negotiate 24-hour breach notification requirement to comply with regulations.",
      },
      {
        category: "Termination",
        severity: "medium",
        title: "Termination Fee for Early Exit",
        description:
          "Cancellation before month 12 results in 50% termination fee of remaining contract value.",
        clause_reference: "Section 4.5",
        recommendation:
          "Negotiate termination fee reduction or add performance-based exit clause.",
      },
      {
        category: "Service Level",
        severity: "low",
        title: "No SLA Credits for Scheduled Maintenance",
        description:
          "Excluded from 99.5% uptime guarantee: all scheduled maintenance windows.",
        clause_reference: "Section 5.2",
        recommendation: "Request limitation to maintenance on weekends/off-hours.",
      },
    ],
    clauses: [
      {
        title: "Service Term and Renewal",
        category: "Term",
        clause_reference: "Section 2",
        description:
          "Initial term of 36 months with automatic annual renewal. Either party may terminate with 60 days written notice.",
        importance: "high",
      },
      {
        title: "Monthly Service Fee",
        category: "Payment",
        clause_reference: "Section 3.1",
        description:
          "Monthly fee of $5,000 USD, billed in advance. Includes support and up to 100 users.",
        importance: "high",
      },
      {
        title: "Service Level Agreement",
        category: "Performance",
        clause_reference: "Section 5",
        description:
          "Vendor commits to 99.5% uptime monthly. Credits provided for downtime exceeding this threshold.",
        importance: "high",
      },
      {
        title: "Data Protection and Security",
        category: "Security",
        clause_reference: "Section 9",
        description:
          "Vendor maintains SOC 2 Type II certification and encrypts data in transit and at rest using AES-256.",
        importance: "high",
      },
      {
        title: "Intellectual Property Rights",
        category: "IP",
        clause_reference: "Section 7",
        description:
          "Your data remains your property. Vendor retains IP rights to software and pre-existing materials.",
        importance: "medium",
      },
      {
        title: "Limitation of Liability",
        category: "Liability",
        clause_reference: "Section 8",
        description:
          "Vendor's total liability capped at 12 months of fees. Excludes indirect damages.",
        importance: "medium",
      },
      {
        title: "Confidentiality",
        category: "Confidentiality",
        clause_reference: "Section 10",
        description:
          "Both parties maintain confidentiality of proprietary information for 3 years post-termination.",
        importance: "medium",
      },
    ],
    recommendations: [
      {
        priority: "high",
        title: "Negotiate cap on indemnification and add performance-based exit clause",
        description: "Legal",
        reason:
          "Current terms expose your company to unlimited liability. Capping indemnification and adding exit flexibility are industry-standard protections.",
      },
      {
        priority: "high",
        title: "Establish internal calendar reminders for the 60-day renewal notice deadline",
        description: "Operations",
        reason:
          "Missing the deadline could lock you into unwanted renewal. Automated reminders reduce operational risk.",
      },
      {
        priority: "medium",
        title: "Verify SOC 2 Type II certificate and conduct annual security audit",
        description: "Security",
        reason:
          "While vendor claims SOC 2 compliance, you should independently verify and maintain audit records.",
      },
      {
        priority: "medium",
        title: "Negotiate 24-hour breach notification requirement",
        description: "Legal",
        reason:
          "Regulatory compliance (GDPR, CCPA) typically requires faster notification than 30 days.",
      },
      {
        priority: "low",
        title: "Request vendor to schedule maintenance windows during off-hours (weekends/nights)",
        description: "Operations",
        reason:
          "Minimizes business impact and demonstrates vendor commitment to availability.",
      },
    ],
    metadata: {
      file_size: 2500000,
      word_count: 8543,
      page_count: 24,
      format: "pdf",
    },
    created_at: new Date().toISOString(),
  };
}

export function generateMockProcessingState(): ProcessingState {
  return {
    status: "idle",
    progress: 0,
    message: "Ready to upload contract",
  };
}

export function generateProcessingStates(): Record<string, ProcessingState> {
  return {
    uploading: {
      status: "uploading",
      progress: 30,
      message: "Uploading contract (service-agreement-2024.pdf)...",
    },
    extracting: {
      status: "processing",
      progress: 45,
      message: "Extracting text from document...",
    },
    analyzing: {
      status: "processing",
      progress: 65,
      message: "Analyzing contract with AI...",
    },
    completed: {
      status: "completed",
      progress: 100,
      message: "Analysis complete",
    },
  };
}
