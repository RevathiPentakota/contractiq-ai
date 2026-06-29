"""DocumentAgent – first node in the contract processing graph.

Responsibility:
    1. Download the raw contract file from Supabase Storage.
    2. Detect file format (PDF or DOCX).
    3. Extract plain text and metadata (file size, page count, word count).
    4. Populate the shared ContractState with extracted_text, metadata,
       and mark processing_status as "document_processed".

Design:
    This agent delegates file I/O and extraction to dedicated services
    (StorageService, DocumentExtractor) to keep the agent thin and
    focused on orchestration.
"""

from __future__ import annotations

from app.agents.base_agent import BaseAgent
from app.core.logging import logger
from app.services.document_extractor import DocumentExtractor
from app.services.storage_service import StorageService
from app.state.contract_state import ContractState


class DocumentAgent(BaseAgent):
    """Download and extract text from contract files in Supabase Storage.

    Supported formats:
    - PDF (via PyMuPDF)
    - DOCX (via python-docx)

    The agent performs synchronous work via service calls. If LangGraph
    detects blocking I/O, wrap this in an executor or convert to async.
    """

    def __init__(self, storage_bucket: str = "contracts") -> None:
        """Initialize the agent with a storage service.

        Args:
            storage_bucket: Name of the Supabase Storage bucket
                           (defaults to "contracts").
        """
        self.storage_service = StorageService(bucket_name=storage_bucket)

    def execute(self, state: ContractState) -> ContractState:
        """Download and extract text from the contract file.

        Args:
            state: Must contain ``storage_path`` and ``file_name``.
                   Typically also contains ``session_id`` and ``contract_id``.

        Returns:
            Updated state with ``extracted_text``, ``metadata``, and
            ``processing_status`` = ``"document_processed"``.

        Raises:
            Captured and added to ``state["errors"]`` so the graph continues.
        """
        file_name = state.get("file_name", "unknown")
        storage_path = state.get("storage_path", "")

        logger.info(
            "[DocumentAgent] Processing file: {file_name} from {path}",
            file_name=file_name,
            path=storage_path,
        )

        try:
            # 1. Download file from Supabase Storage
            logger.debug(
                "[DocumentAgent] Downloading file from storage",
            )
            file_bytes = self.storage_service.download_file(storage_path)

            # 2. Extract text and metadata
            logger.debug(
                "[DocumentAgent] Extracting text from {file}",
                file=file_name,
            )
            extracted_text, metadata = self._extract_text_and_metadata(
                file_bytes, file_name
            )

            logger.info(
                "[DocumentAgent] Extraction complete. "
                "Extracted {words} words, file size {size} bytes.",
                words=metadata.get("word_count", 0),
                size=metadata.get("file_size", 0),
            )

            return ContractState(
                extracted_text=extracted_text,
                metadata=metadata,
                processing_status="document_processed",
            )

        except Exception as err:
            logger.error(
                "[DocumentAgent] Failed to process document: {error}",
                error=str(err),
            )
            error_message = (
                f"Document extraction failed: {str(err)}"
            )
            return ContractState(
                extracted_text="",
                metadata={},
                errors=[error_message],
                processing_status="document_failed",
            )

    def _extract_text_and_metadata(
        self, file_bytes: bytes, file_name: str
    ) -> tuple[str, dict]:
        """Extract text and metadata from document bytes.

        Delegates to DocumentExtractor, which handles PDF and DOCX formats.

        Args:
            file_bytes: Raw file content.
            file_name: Original file name (determines format).

        Returns:
            Tuple of (extracted_text, metadata_dict).

        Raises:
            ValueError: If the file format is unsupported.
            Exception: On extraction errors (corrupt file, etc).
        """
        # Note: This is synchronous but DocumentExtractor is designed to be
        # easily convertible to async if needed. The actual I/O work happens
        # in DocumentExtractor, not here.
        return DocumentExtractor.extract(
            file_bytes,
            file_name,
        )