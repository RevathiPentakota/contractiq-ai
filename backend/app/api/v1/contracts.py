"""Contract upload router – POST /api/v1/contracts/upload.

Handles file upload and contract processing orchestration via LangGraph workflow.
Also provides GET endpoints for retrieving contract history and details.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4, UUID

from fastapi import APIRouter, UploadFile, File, HTTPException, status, Path
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.logging import logger
from app.services.storage_service import StorageService
from app.services.database_service import DatabaseService
from app.state.contract_state import ContractState
from app.workflows.contract_workflow import build_contract_graph

router = APIRouter(tags=["Contracts"])


# ── Response Models ────────────────────────────────────────────────────────────


class AnalysisResult(BaseModel):
    """Contract analysis result returned to the client."""

    contract_id: str
    file_name: str
    created_at: str | None = None
    summary: str
    risks: list[dict]
    clauses: list[dict]
    recommendations: list[dict]
    processing_status: str
    metadata: dict


class UploadResponse(BaseModel):
    """Response for successful contract upload and processing."""

    success: bool
    message: str
    data: AnalysisResult | None = None
    errors: list[str] = []


class ContractSummary(BaseModel):
    """Summary of a contract for list view."""

    contract_id: str
    file_name: str
    processing_status: str
    created_at: str
    file_size: int | None = None
    page_count: int | None = None


class ContractsListResponse(BaseModel):
    """Response containing list of all contracts."""

    success: bool
    data: list[ContractSummary]


class ContractDetailResponse(BaseModel):
    """Response containing complete contract details."""

    success: bool
    data: AnalysisResult | None = None


# ── Upload Endpoint ────────────────────────────────────────────────────────────


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload and process contract",
    description="Upload a PDF contract for AI-powered analysis and processing.",
)
async def upload_contract(file: UploadFile = File(...)) -> UploadResponse:
    """Upload a contract PDF and run the complete analysis workflow.

    The endpoint validates the file, uploads it to Supabase Storage,
    creates a ContractState, and invokes the LangGraph workflow.

    Args:
        file: PDF contract file (multipart/form-data).

    Returns:
        UploadResponse containing:
        - success: Whether processing completed successfully.
        - message: Human-readable status message.
        - data: Complete analysis result if successful.
        - errors: List of error messages if processing failed.

    Raises:
        HTTPException(400): If file validation fails.
        HTTPException(413): If file exceeds size limit.
        HTTPException(500): If processing fails.

    Example:
        >>> import httpx
        >>> with open("contract.pdf", "rb") as f:
        ...     files = {"file": ("contract.pdf", f, "application/pdf")}
        ...     response = httpx.post(
        ...         "http://localhost:8000/api/v1/contracts/upload",
        ...         files=files
        ...     )
        ...     result = response.json()
    """
    request_id = str(uuid4())
    logger.info(
        "[Upload] Starting contract upload (request_id: {id})",
        id=request_id,
    )

    try:
        # ── Validate file ──────────────────────────────────────────────────
        if not file.filename:
            logger.warning("[Upload] No filename provided")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must have a filename",
            )

        if not file.content_type == "application/pdf":
            logger.warning(
                "[Upload] Invalid file type: {type}",
                type=file.content_type,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported",
            )

        settings = get_settings()
        file_data = await file.read()
        file_size_mb = len(file_data) / (1024 * 1024)

        if file_size_mb > settings.max_upload_size_mb:
            logger.warning(
                "[Upload] File exceeds size limit: {size}MB > {limit}MB",
                size=file_size_mb,
                limit=settings.max_upload_size_mb,
            )
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size must not exceed {settings.max_upload_size_mb}MB",
            )

        logger.info(
            "[Upload] File validation passed: {name} ({size}MB)",
            name=file.filename,
            size=round(file_size_mb, 2),
        )

        # ── Upload file to Supabase Storage ────────────────────────────────
        storage_service = StorageService()
        contract_id = str(uuid4())
        storage_path = f"uploads/{contract_id}/{file.filename}"

        logger.debug(
            "[Upload] Uploading to storage: {path}",
            path=storage_path,
        )

        storage_service.upload_file(file_data, storage_path)

        logger.info(
            "[Upload] File uploaded successfully: {path}",
            path=storage_path,
        )

        # ── Create initial ContractState ───────────────────────────────────
        session_id = str(uuid4())
        contract_state: ContractState = {
            "session_id": session_id,
            "contract_id": contract_id,
            "file_name": file.filename,
            "storage_path": storage_path,
            "processing_status": "pending",
            "errors": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(
            "[Upload] Created initial state (contract_id: {id})",
            id=contract_id,
        )

        # ── Invoke LangGraph workflow ──────────────────────────────────────
        logger.info(
            "[Upload] Invoking contract processing workflow",
        )

        graph = build_contract_graph()
        result = graph.invoke(contract_state)

        logger.info(
            "[Upload] Workflow completed with status: {status}",
            status=result.get("processing_status"),
        )

        # ── Check for workflow errors ──────────────────────────────────────
        if result.get("processing_status") == "completed":
            logger.info(
                "[Upload] Contract analysis completed successfully",
            )

            return UploadResponse(
                success=True,
                message="Contract processed successfully",
                data=AnalysisResult(
                    contract_id=result.get("contract_id", contract_id),
                    file_name=result.get("file_name", file.filename),
                    created_at=result.get("created_at"),
                    summary=result.get("summary", ""),
                    risks=result.get("risks", []),
                    clauses=result.get("clauses", []),
                    recommendations=result.get("recommendations", []),
                    processing_status=result.get("processing_status", "completed"),
                    metadata=result.get("metadata", {}),
                ),
                errors=result.get("errors", []),
            )
        else:
            # Workflow failed or is incomplete
            errors = result.get("errors", ["Unknown processing error"])
            logger.error(
                "[Upload] Workflow failed with status: {status}, errors: {errors}",
                status=result.get("processing_status"),
                errors=errors,
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Contract processing failed: {'; '.join(errors)}",
            )

    except HTTPException as http_err:
        logger.warning("[Upload] HTTP error: {detail}", detail=http_err.detail)
        raise
    except Exception as err:
        logger.error(
            "[Upload] Unexpected error: {error}",
            error=str(err),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during processing",
        ) from err


# ── History Endpoints ──────────────────────────────────────────────────────────


@router.get(
    "",
    response_model=ContractsListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all contracts",
    description="Retrieve all uploaded contracts ordered by creation date (newest first).",
)
def list_contracts() -> ContractsListResponse:
    """Retrieve all contracts with key metadata.

    Returns contracts ordered by creation date (newest first).

    Returns:
        ContractsListResponse containing:
        - success: Whether the request succeeded.
        - data: List of ContractSummary objects.

    Raises:
        HTTPException(500): On database errors.

    Example:
        >>> response = requests.get("http://localhost:8000/api/v1/contracts")
        >>> contracts = response.json()["data"]
        >>> for contract in contracts:
        ...     print(contract["file_name"])
    """
    logger.info("[Contracts] Listing all contracts")

    try:
        database_service = DatabaseService()
        contracts = database_service.get_contracts()

        logger.info(
            "[Contracts] Successfully retrieved {count} contracts",
            count=len(contracts),
        )

        return ContractsListResponse(
            success=True,
            data=[
                ContractSummary(
                    contract_id=c["contract_id"],
                    file_name=c["file_name"],
                    processing_status=c["processing_status"],
                    created_at=c["created_at"],
                    file_size=c["file_size"],
                    page_count=c["page_count"],
                )
                for c in contracts
            ],
        )

    except Exception as err:
        logger.error(
            "[Contracts] Failed to list contracts: {error}",
            error=str(err),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve contracts",
        ) from err


@router.get(
    "/{contract_id}",
    response_model=ContractDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get contract details",
    description="Retrieve complete analysis for a specific contract.",
)
def get_contract(
    contract_id: str = Path(..., description="UUID of the contract"),
) -> ContractDetailResponse:
    """Retrieve complete contract analysis by ID.

    Retrieves all analysis data including summary, risks, clauses,
    and recommendations for the specified contract.

    Args:
        contract_id: UUID of the contract.

    Returns:
        ContractDetailResponse containing:
        - success: Whether the contract was found.
        - data: AnalysisResult with all analysis data.

    Raises:
        HTTPException(400): If contract_id is not a valid UUID.
        HTTPException(404): If contract not found.
        HTTPException(500): On database errors.

    Example:
        >>> contract_id = "550e8400-e29b-41d4-a716-446655440000"
        >>> response = requests.get(
        ...     f"http://localhost:8000/api/v1/contracts/{contract_id}"
        ... )
        >>> analysis = response.json()["data"]
        >>> print(analysis["summary"])
    """
    # ── Validate contract_id is a valid UUID ───────────────────────────────
    try:
        UUID(contract_id)
    except ValueError:
        logger.warning(
            "[Contracts] Invalid contract_id format: {id}",
            id=contract_id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid contract ID format. Must be a valid UUID, got: {contract_id}",
        )

    logger.info(
        "[Contracts] Retrieving contract | contract_id={id}",
        id=contract_id,
    )

    try:
        database_service = DatabaseService()
        contract_data = database_service.get_contract(contract_id)

        logger.info(
            "[Contracts] Successfully retrieved contract | contract_id={id}",
            id=contract_id,
        )

        return ContractDetailResponse(
            success=True,
            data=AnalysisResult(
                contract_id=contract_data["contract_id"],
                file_name=contract_data["file_name"],
                created_at=contract_data.get("created_at"),
                summary=contract_data["summary"],
                risks=contract_data["risks"],
                clauses=contract_data["clauses"],
                recommendations=contract_data["recommendations"],
                processing_status=contract_data["processing_status"],
                metadata=contract_data["metadata"],
            ),
        )

    except ValueError as err:
        logger.warning(
            "[Contracts] Contract not found | contract_id={id}",
            id=contract_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
    except Exception as err:
        logger.error(
            "[Contracts] Failed to retrieve contract {id}: {error}",
            id=contract_id,
            error=str(err),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve contract",
        ) from err
