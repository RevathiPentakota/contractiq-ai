"""Document extractor service – text extraction from PDF and DOCX.

Abstracts PDF and DOCX extraction logic so DocumentAgent can remain
focused on orchestration rather than file format details.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import fitz  # PyMuPDF
from docx import Document

from app.core.logging import logger


class DocumentExtractor:
    """Extract text and metadata from PDF and DOCX documents.

    Supported formats:
    - PDF (via PyMuPDF / fitz)
    - DOCX (via python-docx)
    """

    SUPPORTED_EXTENSIONS = {".pdf", ".docx"}

    @staticmethod
    def get_file_extension(file_name: str) -> str:
        """Extract the lowercase file extension.

        Args:
            file_name: Name of the file (e.g. "contract.pdf").

        Returns:
            Lowercase extension including the dot (e.g. ".pdf").

        Raises:
            ValueError: If the file has no extension.
        """
        ext = Path(file_name).suffix.lower()
        if not ext:
            raise ValueError(f"File has no extension: {file_name}")
        return ext

    @staticmethod
    def extract(
        file_bytes: bytes,
        file_name: str
    ) -> tuple[str, dict[str, object]]:
        """Extract text and metadata from a document.

        Args:
            file_bytes: Raw file content.
            file_name: Original file name (used to detect format).

        Returns:
            Tuple of (extracted_text, metadata_dict).
            Metadata always includes "file_size" and "word_count".
            PDF adds "page_count"; DOCX does not.

        Raises:
            ValueError: If the file format is not supported.
            Exception: On extraction errors (corrupt file, etc).

        Example:
            >>> text, meta = await DocumentExtractor.extract(
            ...     file_bytes, "contract.pdf"
            ... )
            >>> meta["file_size"]
            12345
            >>> meta["page_count"]  # PDF only
            5
        """
        ext = DocumentExtractor.get_file_extension(file_name)

        if ext == ".pdf":
            return DocumentExtractor._extract_pdf(file_bytes, file_name)
        elif ext == ".docx":
            return DocumentExtractor._extract_docx(file_bytes, file_name)
        else:
            raise ValueError(
                f"Unsupported file format: {ext}. "
                f"Supported: {', '.join(DocumentExtractor.SUPPORTED_EXTENSIONS)}"
            )

    @staticmethod
    def _extract_pdf(file_bytes: bytes, file_name: str) -> tuple[str, dict]:
        """Extract text and metadata from a PDF document.

        Args:
            file_bytes: Raw PDF bytes.
            file_name: Name of the PDF file.

        Returns:
            Tuple of (text, metadata).

        Raises:
            Exception: On PDF parsing errors.
        """
        logger.debug(
            "[DocumentExtractor] Extracting PDF: {file}",
            file=file_name,
        )

        try:
            pdf_bytes_io = BytesIO(file_bytes)
            pdf_document = fitz.open(stream=pdf_bytes_io, filetype="pdf")

            # Extract all text
            text_parts = []
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                text = page.get_text()
                text_parts.append(text)

            full_text = "\n".join(text_parts)
            page_count = len(pdf_document)

            pdf_document.close()

            word_count = len(full_text.split())
            metadata = {
                "file_size": len(file_bytes),
                "page_count": page_count,
                "word_count": word_count,
                "format": "pdf",
            }

            logger.info(
                "[DocumentExtractor] PDF extracted: {pages} pages, "
                "{words} words",
                pages=page_count,
                words=word_count,
            )

            return full_text, metadata

        except Exception as err:
            logger.error(
                "[DocumentExtractor] PDF extraction failed: {error}",
                error=str(err),
            )
            raise

    @staticmethod
    def _extract_docx(file_bytes: bytes, file_name: str) -> tuple[str, dict]:
        """Extract text and metadata from a DOCX document.

        Args:
            file_bytes: Raw DOCX bytes.
            file_name: Name of the DOCX file.

        Returns:
            Tuple of (text, metadata).

        Raises:
            Exception: On DOCX parsing errors.
        """
        logger.debug(
            "[DocumentExtractor] Extracting DOCX: {file}",
            file=file_name,
        )

        try:
            docx_bytes_io = BytesIO(file_bytes)
            docx_document = Document(docx_bytes_io)

            # Extract all text from paragraphs
            text_parts = []
            for paragraph in docx_document.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)

            full_text = "\n".join(text_parts)
            word_count = len(full_text.split())

            metadata = {
                "file_size": len(file_bytes),
                "word_count": word_count,
                "format": "docx",
            }

            logger.info(
                "[DocumentExtractor] DOCX extracted: {words} words",
                words=word_count,
            )

            return full_text, metadata

        except Exception as err:
            logger.error(
                "[DocumentExtractor] DOCX extraction failed: {error}",
                error=str(err),
            )
            raise
