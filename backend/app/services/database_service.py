"""Database service – Persistence layer for contract analysis results.

Handles persisting contract analysis data to PostgreSQL (via Supabase).
Abstracts away database connection and SQL details so PersistenceAgent
remains thin and easily testable.

The service uses SQLAlchemy async engine configured in Settings, and
provides high-level methods for saving analysis results.
"""

from __future__ import annotations

import uuid
from typing import Any

from loguru import logger

from app.core.config import get_settings
from app.state.contract_state import ContractState
from supabase import Client, create_client


class DatabaseService:
    """Service for persisting contract analysis to PostgreSQL.

    Handles:
    - Saving contract metadata (file name, storage path, etc.)
    - Saving executive summary
    - Saving identified risks
    - Saving extracted clauses
    - Saving actionable recommendations

    The service is stateless; database connections are managed via
    SQLAlchemy async engine configured at application startup.

    Implementation Notes:
    - Currently placeholder methods that log the save operation.
    - Full schema and database operations will be implemented
      when models are defined.
    - All methods are synchronous but designed to work with async agents.
    """

    def __init__(self) -> None:
        """Initialize the database service.

        Database connection details are loaded from Settings at call time,
        allowing environment changes to be respected.
        """
        self.settings = get_settings()
        self._client: Client = create_client(
            self.settings.supabase_url,
            self.settings.supabase_service_role_key,
        )

    def save_contract_analysis(
        self,
        state: ContractState,
    ) -> None:
        """Persist complete contract analysis to database.

        Saves all contract analysis results including summary, risks,
        clauses, and recommendations to their respective database tables.

        Args:
            state: Complete ContractState with all analysis results.
                   Must contain: contract_id, file_name, storage_path,
                   metadata, summary, risks, clauses, recommendations.

        Raises:
            ValueError: If required state fields are missing.
            Exception: On database connection or query errors.

        Example:
            >>> service = DatabaseService()
            >>> state = ContractState(contract_id="...", summary="...", ...)
            >>> service.save_contract_analysis(state)
        """
        contract_id = state.get("contract_id", "unknown")
        file_name = state.get("file_name", "unknown")
        storage_path = state.get("storage_path", "unknown")
        summary = state.get("summary", "")
        risks = state.get("risks", [])
        clauses = state.get("clauses", [])
        recommendations = state.get("recommendations", [])
        metadata = state.get("metadata", {})

        logger.info(
            "[DatabaseService] Saving contract analysis | contract_id={contract_id} | "
            "file_name={file_name} | summary_length={summary_len} | "
            "risks={risk_count} | clauses={clause_count} | "
            "recommendations={rec_count}",
            contract_id=contract_id,
            file_name=file_name,
            summary_len=len(summary),
            risk_count=len(risks),
            clause_count=len(clauses),
            rec_count=len(recommendations),
        )

        try:
            self._save_contract_metadata(
                contract_id=contract_id,
                file_name=file_name,
                storage_path=storage_path,
                metadata=metadata,
                processing_status=state.get("processing_status", "pending"),
            )

            self._save_summary(
                contract_id=contract_id,
                summary=summary,
            )

            self._save_risks(
                contract_id=contract_id,
                risks=risks,
            )

            self._save_clauses(
                contract_id=contract_id,
                clauses=clauses,
            )

            self._save_recommendations(
                contract_id=contract_id,
                recommendations=recommendations,
            )

            logger.info(
                "[DatabaseService] Contract analysis saved successfully | "
                "contract_id={contract_id}",
                contract_id=contract_id,
            )

        except Exception as err:
            logger.error(
                "[DatabaseService] Failed to save contract analysis: {error}",
                error=str(err),
            )
            raise

    def _save_contract_metadata(
            self,
            contract_id: str,
            file_name: str,
            storage_path: str,
            metadata: dict[str, Any],
            processing_status: str,
        ) -> None:
        """Save contract metadata."""

        logger.debug(
            "[DatabaseService] Saving contract metadata | contract_id={contract_id}",
            contract_id=contract_id,
        )

        record = {
            "contractid": contract_id,
            "filename": file_name,
            "storagepath": storage_path,
            "filesize": metadata.get("file_size"),
            "pagecount": metadata.get("page_count"),
            "wordcount": metadata.get("word_count"),
            "fileformat": metadata.get("format"),
            "processingstatus": processing_status,
        }

        self._client.table("contracts").insert(record).execute()

        logger.info(
            "[DatabaseService] Contract metadata saved | contract_id={contract_id}",
            contract_id=contract_id,
        )

    def _save_summary(
        self,
        contract_id: str,
        summary: str,
    ) -> None:
        """Save contract summary to database.

        Args:
            contract_id: Unique contract identifier.
            summary: Executive summary text.
        """
        logger.debug(
            "[DatabaseService] Saving contract summary | contract_id={contract_id}",
            contract_id=contract_id,
        )

        record = {
            "summaryid": str(uuid.uuid4()),
            "contractid": contract_id,
            "summary": summary,
        }

        self._client.table("contractsummaries").insert(record).execute()

        logger.info(
            "[DatabaseService] Contract summary saved | contract_id={contract_id}",
            contract_id=contract_id,
        )

    def _save_risks(
        self,
        contract_id: str,
        risks: list[dict[str, Any]],
    ) -> None:
        """Save identified risks to database.

        Args:
            contract_id: Unique contract identifier.
            risks: List of risk dictionaries with category, severity, etc.
        """
        logger.debug(
            "[DatabaseService] Saving contract risks | contract_id={contract_id} | "
            "risk_count={count}",
            contract_id=contract_id,
            count=len(risks),
        )

        for risk in risks:
            record = {
                "riskid": str(uuid.uuid4()),
                "contractid": contract_id,
                "category": risk.get("category"),
                "severity": risk.get("severity"),
                "title": risk.get("title"),
                "description": risk.get("description"),
                "clausereference": risk.get("clause_reference"),
                "recommendation": risk.get("recommendation"),
            }

            self._client.table("contractrisks").insert(record).execute()

        logger.info(
            "[DatabaseService] Contract risks saved | contract_id={contract_id} | "
            "risk_count={count}",
            contract_id=contract_id,
            count=len(risks),
        )

    def _save_clauses(
        self,
        contract_id: str,
        clauses: list[dict[str, Any]],
    ) -> None:
        """Save extracted clauses to database.

        Args:
            contract_id: Unique contract identifier.
            clauses: List of clause dictionaries with title, category, etc.
        """
        logger.debug(
            "[DatabaseService] Saving contract clauses | contract_id={contract_id} | "
            "clause_count={count}",
            contract_id=contract_id,
            count=len(clauses),
        )

        for clause in clauses:
            record = {
                "clauseid": str(uuid.uuid4()),
                "contractid": contract_id,
                "title": clause.get("title"),
                "category": clause.get("category"),
                "clausereference": clause.get("clause_reference"),
                "description": clause.get("description"),
                "importance": clause.get("importance"),
            }

            self._client.table("contractclauses").insert(record).execute()

        logger.info(
            "[DatabaseService] Contract clauses saved | contract_id={contract_id} | "
            "clause_count={count}",
            contract_id=contract_id,
            count=len(clauses),
        )

    def _save_recommendations(
        self,
        contract_id: str,
        recommendations: list[dict[str, Any]],
    ) -> None:
        """Save actionable recommendations to database.

        Args:
            contract_id: Unique contract identifier.
            recommendations: List of recommendation dictionaries.
        """
        logger.debug(
            "[DatabaseService] Saving recommendations | contract_id={contract_id} | "
            "recommendation_count={count}",
            contract_id=contract_id,
            count=len(recommendations),
        )

        for rec in recommendations:
            record = {
                "recommendationid": str(uuid.uuid4()),
                "contractid": contract_id,
                "priority": rec.get("priority"),
                "title": rec.get("title"),
                "description": rec.get("description"),
                "reason": rec.get("reason"),
            }

            self._client.table("contractrecommendations").insert(record).execute()

        logger.info(
            "[DatabaseService] Recommendations saved | contract_id={contract_id} | "
            "recommendation_count={count}",
            contract_id=contract_id,
            count=len(recommendations),
        )

    def get_contracts(self) -> list[dict[str, Any]]:
        """Retrieve all contracts ordered by creation date (newest first).

        Returns:
            List of contract dictionaries containing:
            - contract_id
            - file_name
            - processing_status
            - created_at
            - file_size
            - page_count

        Example:
            >>> service = DatabaseService()
            >>> contracts = service.get_contracts()
            >>> for contract in contracts:
            ...     print(contract["file_name"])
        """
        logger.debug("[DatabaseService] Retrieving all contracts")

        try:
            response = (
                self._client.table("contracts")
                .select(
                    "contractid, filename, processingstatus, createdat, filesize, pagecount"
                )
                .order("createdat", desc=True)
                .execute()
            )

            contracts = [
                {
                    "contract_id": record["contractid"],
                    "file_name": record["filename"],
                    "processing_status": record["processingstatus"],
                    "created_at": record["createdat"],
                    "file_size": record["filesize"],
                    "page_count": record["pagecount"],
                }
                for record in response.data
            ]

            logger.info(
                "[DatabaseService] Retrieved {count} contracts",
                count=len(contracts),
            )

            return contracts

        except Exception as err:
            logger.error(
                "[DatabaseService] Failed to retrieve contracts: {error}",
                error=str(err),
            )
            raise

    def get_contract(self, contract_id: str) -> dict[str, Any]:
        """Retrieve complete contract analysis by ID.

        Joins data from contracts, contractsummaries, contractrisks,
        contractclauses, and contractrecommendations tables.

        Args:
            contract_id: UUID of the contract.

        Returns:
            Dictionary containing:
            - contract_id
            - file_name
            - summary
            - risks
            - clauses
            - recommendations
            - processing_status
            - metadata (file_size, page_count, word_count, format)

        Raises:
            ValueError: If contract not found.
            Exception: On database errors.

        Example:
            >>> service = DatabaseService()
            >>> contract = service.get_contract("550e8400-e29b-41d4-a716-446655440000")
            >>> print(contract["summary"])
        """
        logger.debug(
            "[DatabaseService] Retrieving contract | contract_id={contract_id}",
            contract_id=contract_id,
        )

        try:
            # Get contract metadata
            contract_response = (
                self._client.table("contracts")
                .select("*")
                .eq("contractid", contract_id)
                .execute()
            )

            if not contract_response.data:
                logger.warning(
                    "[DatabaseService] Contract not found | contract_id={contract_id}",
                    contract_id=contract_id,
                )
                raise ValueError(f"Contract not found: {contract_id}")

            contract = contract_response.data[0]

            # Get summary
            summary_response = (
                self._client.table("contractsummaries")
                .select("summary")
                .eq("contractid", contract_id)
                .execute()
            )
            summary = summary_response.data[0]["summary"] if summary_response.data else ""

            # Get risks
            risks_response = (
                self._client.table("contractrisks")
                .select("*")
                .eq("contractid", contract_id)
                .execute()
            )
            risks = [
                {
                    "category": r["category"],
                    "severity": r["severity"],
                    "title": r["title"],
                    "description": r["description"],
                    "clause_reference": r["clausereference"],
                    "recommendation": r["recommendation"],
                }
                for r in risks_response.data
            ]

            # Get clauses
            clauses_response = (
                self._client.table("contractclauses")
                .select("*")
                .eq("contractid", contract_id)
                .execute()
            )
            clauses = [
                {
                    "title": c["title"],
                    "category": c["category"],
                    "clause_reference": c["clausereference"],
                    "description": c["description"],
                    "importance": c["importance"],
                }
                for c in clauses_response.data
            ]

            # Get recommendations
            recs_response = (
                self._client.table("contractrecommendations")
                .select("*")
                .eq("contractid", contract_id)
                .execute()
            )
            recommendations = [
                {
                    "priority": r["priority"],
                    "title": r["title"],
                    "description": r["description"],
                    "reason": r["reason"],
                }
                for r in recs_response.data
            ]

            logger.info(
                "[DatabaseService] Contract retrieved | contract_id={contract_id} | "
                "summary_length={summary_len} | risks={risk_count} | clauses={clause_count} | "
                "recommendations={rec_count}",
                contract_id=contract_id,
                summary_len=len(summary),
                risk_count=len(risks),
                clause_count=len(clauses),
                rec_count=len(recommendations),
            )

            return {
                "contract_id": contract["contractid"],
                "file_name": contract["filename"],
                "created_at": contract.get("createdat"),
                "summary": summary,
                "risks": risks,
                "clauses": clauses,
                "recommendations": recommendations,
                "processing_status": contract["processingstatus"],
                "metadata": {
                    "file_size": contract["filesize"],
                    "page_count": contract["pagecount"],
                    "word_count": contract.get("wordcount"),
                    "format": contract.get("fileformat"),
                },
            }

        except ValueError:
            raise
        except Exception as err:
            logger.error(
                "[DatabaseService] Failed to retrieve contract {contract_id}: {error}",
                contract_id=contract_id,
                error=str(err),
            )
            raise
