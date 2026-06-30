"""Tests for the contract upload API endpoint."""

from __future__ import annotations

import json
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.state.contract_state import ContractState


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def sample_pdf():
    """Generate minimal valid PDF bytes for testing."""
    pdf_header = b"%PDF-1.4\n"
    pdf_obj = b"1 0 obj\n<</Type /Catalog /Pages 2 0 R>>\nendobj\n"
    pdf_footer = b"xref\n0 1\n0000000000 65535 f\ntrailer\n<</Size 2 /Root 1 0 R>>\nstartxref\n44\n%%EOF"
    return pdf_header + pdf_obj + pdf_footer


class TestUploadContractEndpoint:
    """Tests for POST /api/v1/contracts/upload."""

    def test_upload_success(self, client, sample_pdf):
        """Test successful contract upload and processing."""
        with patch("app.api.v1.contracts.StorageService") as mock_storage_cls, \
             patch("app.api.v1.contracts.build_contract_graph") as mock_graph_builder:

            # Mock storage
            mock_storage = MagicMock()
            mock_storage_cls.return_value = mock_storage
            mock_storage.upload_file.return_value = "uploads/contract-123/test.pdf"

            # Mock workflow
            mock_graph = MagicMock()
            mock_graph_builder.return_value = mock_graph

            # Mock successful workflow result
            mock_graph.invoke.return_value = {
                "contract_id": "contract-123",
                "file_name": "test.pdf",
                "summary": "Test summary",
                "risks": [{"title": "Risk 1", "severity": "high"}],
                "clauses": [{"title": "Clause 1", "category": "Payment"}],
                "recommendations": [{"recommendation": "Negotiate terms", "priority": "high"}],
                "processing_status": "completed",
                "errors": [],
                "metadata": {"word_count": 100},
            }

            # Make request
            response = client.post(
                "/api/v1/contracts/upload",
                files={"file": ("test.pdf", BytesIO(sample_pdf), "application/pdf")},
            )

            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Contract processed successfully"
            assert data["data"]["contract_id"] == "contract-123"
            assert data["data"]["summary"] == "Test summary"
            assert len(data["data"]["risks"]) == 1
            assert len(data["data"]["clauses"]) == 1
            assert len(data["data"]["recommendations"]) == 1

    def test_upload_missing_file(self, client):
        """Test upload with no file."""
        response = client.post("/api/v1/contracts/upload")
        assert response.status_code == 422  # Unprocessable Entity

    def test_upload_invalid_content_type(self, client, sample_pdf):
        """Test upload with non-PDF file."""
        response = client.post(
            "/api/v1/contracts/upload",
            files={"file": ("test.txt", BytesIO(sample_pdf), "text/plain")},
        )

        assert response.status_code == 400
        data = response.json()
        assert "PDF" in data["detail"]

    def test_upload_file_too_large(self, client):
        """Test upload with file exceeding size limit."""
        with patch("app.api.v1.contracts.get_settings") as mock_settings:
            # Set max size to 1MB for testing
            mock_settings.return_value.max_upload_size_mb = 1

            # Create large file (2MB)
            large_file = BytesIO(b"x" * (2 * 1024 * 1024))

            response = client.post(
                "/api/v1/contracts/upload",
                files={"file": ("large.pdf", large_file, "application/pdf")},
            )

            assert response.status_code == 413  # Request Entity Too Large
            data = response.json()
            assert "must not exceed" in data["detail"]

    def test_upload_storage_error(self, client, sample_pdf):
        """Test upload when storage fails."""
        with patch("app.api.v1.contracts.StorageService") as mock_storage_cls:
            mock_storage = MagicMock()
            mock_storage_cls.return_value = mock_storage
            mock_storage.upload_file.side_effect = Exception("Storage error")

            response = client.post(
                "/api/v1/contracts/upload",
                files={"file": ("test.pdf", BytesIO(sample_pdf), "application/pdf")},
            )

            assert response.status_code == 500
            data = response.json()
            assert "error" in data["detail"].lower()

    def test_upload_workflow_error(self, client, sample_pdf):
        """Test upload when workflow processing fails."""
        with patch("app.api.v1.contracts.StorageService") as mock_storage_cls, \
             patch("app.api.v1.contracts.build_contract_graph") as mock_graph_builder:

            # Mock storage
            mock_storage = MagicMock()
            mock_storage_cls.return_value = mock_storage
            mock_storage.upload_file.return_value = "uploads/contract-123/test.pdf"

            # Mock failed workflow
            mock_graph = MagicMock()
            mock_graph_builder.return_value = mock_graph
            mock_graph.invoke.return_value = {
                "processing_status": "failed",
                "errors": ["Document extraction failed"],
            }

            response = client.post(
                "/api/v1/contracts/upload",
                files={"file": ("test.pdf", BytesIO(sample_pdf), "application/pdf")},
            )

            assert response.status_code == 500
            data = response.json()
            assert "processing failed" in data["detail"].lower()

    def test_upload_empty_results(self, client, sample_pdf):
        """Test upload with empty analysis results."""
        with patch("app.api.v1.contracts.StorageService") as mock_storage_cls, \
             patch("app.api.v1.contracts.build_contract_graph") as mock_graph_builder:

            # Mock storage
            mock_storage = MagicMock()
            mock_storage_cls.return_value = mock_storage
            mock_storage.upload_file.return_value = "uploads/contract-123/test.pdf"

            # Mock workflow with empty results
            mock_graph = MagicMock()
            mock_graph_builder.return_value = mock_graph
            mock_graph.invoke.return_value = {
                "contract_id": "contract-123",
                "file_name": "test.pdf",
                "summary": "",
                "risks": [],
                "clauses": [],
                "recommendations": [],
                "processing_status": "completed",
                "errors": [],
                "metadata": {},
            }

            response = client.post(
                "/api/v1/contracts/upload",
                files={"file": ("test.pdf", BytesIO(sample_pdf), "application/pdf")},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["summary"] == ""
            assert data["data"]["risks"] == []

    def test_upload_response_structure(self, client, sample_pdf):
        """Test that upload response has correct structure."""
        with patch("app.api.v1.contracts.StorageService") as mock_storage_cls, \
             patch("app.api.v1.contracts.build_contract_graph") as mock_graph_builder:

            # Mock storage and workflow
            mock_storage = MagicMock()
            mock_storage_cls.return_value = mock_storage
            mock_storage.upload_file.return_value = "uploads/contract-123/test.pdf"

            mock_graph = MagicMock()
            mock_graph_builder.return_value = mock_graph
            mock_graph.invoke.return_value = {
                "contract_id": "contract-123",
                "file_name": "test.pdf",
                "summary": "Summary",
                "risks": [],
                "clauses": [],
                "recommendations": [],
                "processing_status": "completed",
                "errors": [],
                "metadata": {},
            }

            response = client.post(
                "/api/v1/contracts/upload",
                files={"file": ("test.pdf", BytesIO(sample_pdf), "application/pdf")},
            )

            assert response.status_code == 200
            data = response.json()

            # Verify response structure
            assert "success" in data
            assert "message" in data
            assert "data" in data
            assert "errors" in data


class TestContractDetailsEndpoint:
    """Tests for GET /api/v1/contracts/{contract_id}."""

    def test_get_contract_with_invalid_uuid_format(self, client):
        """Test that GET with invalid UUID format returns 400 Bad Request."""
        # "upload" is not a valid UUID, should return 400
        response = client.get("/api/v1/contracts/upload")
        assert response.status_code == 400
        data = response.json()
        assert "Invalid contract ID format" in data["detail"]

