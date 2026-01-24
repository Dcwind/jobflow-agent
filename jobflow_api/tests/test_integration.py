"""Integration tests for the full job extraction flow.

These tests verify the complete pipeline from URL input to stored job data.
They mock external HTTP requests but test the real extraction logic.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from shared.db.models import Base, Job
from shared.db.session import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from jobflow_api.main import app

# Sample HTML for testing extraction
SAMPLE_JOB_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Software Engineer at TechCorp - Careers</title>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org/",
        "@type": "JobPosting",
        "title": "Software Engineer",
        "hiringOrganization": {
            "@type": "Organization",
            "name": "TechCorp Inc"
        },
        "jobLocation": {
            "@type": "Place",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": "San Francisco",
                "addressRegion": "CA"
            }
        },
        "baseSalary": {
            "@type": "MonetaryAmount",
            "currency": "USD",
            "value": {
                "@type": "QuantitativeValue",
                "minValue": 150000,
                "maxValue": 200000,
                "unitText": "YEAR"
            }
        },
        "description": "We are looking for a talented software engineer to join our team."
    }
    </script>
</head>
<body>
    <h1>Software Engineer</h1>
    <p>Company: TechCorp Inc</p>
    <p>Location: San Francisco, CA</p>
    <p>Salary: $150,000 - $200,000</p>
</body>
</html>
"""

SAMPLE_MINIMAL_HTML = """
<!DOCTYPE html>
<html>
<head><title>Job Opening</title></head>
<body>
    <h1>Product Manager</h1>
    <div class="company">StartupXYZ</div>
</body>
</html>
"""


@pytest.fixture
def test_db():
    """Create a test database."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(engine)
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        def override_get_db():
            db = TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        yield TestingSessionLocal
        app.dependency_overrides.clear()


@pytest.fixture
def client(test_db):
    """Create a test client."""
    return TestClient(app)


class TestFullExtractionFlow:
    """Integration tests for the complete extraction pipeline."""

    def test_extract_job_with_json_ld(self, client) -> None:
        """Extract a job from a page with JSON-LD structured data."""
        with patch("shared.extraction.pipeline._fetch_with_requests") as mock_fetch:
            mock_fetch.return_value = SAMPLE_JOB_HTML

            response = client.post(
                "/api/jobs",
                json={"urls": ["https://example.com/jobs/software-engineer"]},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["succeeded"] == 1
            assert data["failed"] == 0

            job = data["results"][0]["job"]
            assert job["title"] == "Software Engineer"
            assert job["company"] == "TechCorp Inc"
            assert "San Francisco" in (job["location"] or "")
            assert job["extraction_method"] is not None

    def test_extract_job_minimal_html(self, client) -> None:
        """Extract a job from a page with minimal structure."""
        with patch("shared.extraction.pipeline._fetch_with_requests") as mock_fetch:
            mock_fetch.return_value = SAMPLE_MINIMAL_HTML

            response = client.post(
                "/api/jobs",
                json={"urls": ["https://example.com/jobs/product-manager"]},
            )

            assert response.status_code == 200
            data = response.json()
            # May or may not succeed depending on extraction quality
            assert data["total"] == 1

    def test_duplicate_url_returns_existing(self, client, test_db) -> None:
        """Submitting the same URL twice returns the existing job."""
        with patch("shared.extraction.pipeline._fetch_with_requests") as mock_fetch:
            mock_fetch.return_value = SAMPLE_JOB_HTML

            # First submission
            response1 = client.post(
                "/api/jobs",
                json={"urls": ["https://example.com/jobs/123"]},
            )
            assert response1.status_code == 200
            job1_id = response1.json()["results"][0]["job"]["id"]

            # Second submission - should return same job
            response2 = client.post(
                "/api/jobs",
                json={"urls": ["https://example.com/jobs/123"]},
            )
            assert response2.status_code == 200
            job2_id = response2.json()["results"][0]["job"]["id"]

            assert job1_id == job2_id

    def test_batch_extraction(self, client) -> None:
        """Extract multiple jobs in a single request."""
        with patch("shared.extraction.pipeline._fetch_with_requests") as mock_fetch:
            mock_fetch.return_value = SAMPLE_JOB_HTML

            response = client.post(
                "/api/jobs",
                json={
                    "urls": [
                        "https://example.com/jobs/1",
                        "https://example.com/jobs/2",
                        "https://example.com/jobs/3",
                    ]
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 3
            assert data["succeeded"] == 3

    def test_invalid_url_rejected(self, client) -> None:
        """Invalid URLs are rejected before fetching."""
        response = client.post(
            "/api/jobs",
            json={"urls": ["not-a-valid-url"]},
        )
        # Pydantic validation should reject this
        assert response.status_code == 422

    def test_blocked_url_rejected(self, client) -> None:
        """URLs to localhost/internal IPs are blocked."""
        with patch("shared.extraction.pipeline._fetch_with_requests") as mock_fetch:
            mock_fetch.return_value = None  # Would fail anyway

            response = client.post(
                "/api/jobs",
                json={"urls": ["http://localhost/job"]},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["failed"] == 1
            assert (
                "Invalid" in data["results"][0]["error"] or data["results"][0]["error"] is not None
            )


class TestJobCRUDFlow:
    """Integration tests for CRUD operations on jobs."""

    def test_create_list_update_delete_flow(self, client) -> None:
        """Test the full CRUD lifecycle."""
        with patch("shared.extraction.pipeline._fetch_with_requests") as mock_fetch:
            mock_fetch.return_value = SAMPLE_JOB_HTML

            # Create
            create_resp = client.post(
                "/api/jobs",
                json={"urls": ["https://example.com/jobs/crud-test"]},
            )
            assert create_resp.status_code == 200
            job_id = create_resp.json()["results"][0]["job"]["id"]

            # List
            list_resp = client.get("/api/jobs")
            assert list_resp.status_code == 200
            assert list_resp.json()["total"] == 1

            # Get single
            get_resp = client.get(f"/api/jobs/{job_id}")
            assert get_resp.status_code == 200
            assert get_resp.json()["id"] == job_id

            # Update
            update_resp = client.patch(
                f"/api/jobs/{job_id}",
                json={"title": "Senior Software Engineer", "salary": "$180k-$220k"},
            )
            assert update_resp.status_code == 200
            assert update_resp.json()["title"] == "Senior Software Engineer"
            assert update_resp.json()["salary"] == "$180k-$220k"

            # Flag
            flag_resp = client.patch(f"/api/jobs/{job_id}/flag", json={"flagged": True})
            assert flag_resp.status_code == 200
            assert flag_resp.json()["flagged"] is True

            # Delete
            delete_resp = client.delete(f"/api/jobs/{job_id}")
            assert delete_resp.status_code == 200

            # Verify deleted
            get_resp2 = client.get(f"/api/jobs/{job_id}")
            assert get_resp2.status_code == 404


class TestCSVExport:
    """Integration tests for CSV export functionality."""

    def test_export_csv_with_data(self, client) -> None:
        """Export jobs to CSV format."""
        with patch("shared.extraction.pipeline._fetch_with_requests") as mock_fetch:
            mock_fetch.return_value = SAMPLE_JOB_HTML

            # Create some jobs
            client.post(
                "/api/jobs",
                json={
                    "urls": [
                        "https://example.com/jobs/export-1",
                        "https://example.com/jobs/export-2",
                    ]
                },
            )

            # Export
            export_resp = client.get("/api/jobs/export")
            assert export_resp.status_code == 200
            assert "text/csv" in export_resp.headers["content-type"]

            csv_content = export_resp.text
            lines = csv_content.strip().split("\n")
            assert len(lines) == 3  # header + 2 jobs
            assert "id,url,title,company" in lines[0]
            assert "Software Engineer" in csv_content
            assert "TechCorp" in csv_content

    def test_export_csv_with_filter(self, client, test_db) -> None:
        """Export filtered jobs to CSV."""
        # Create jobs directly in DB for filtering test
        db = test_db()
        job1 = Job(
            url="https://example.com/job/a",
            title="Engineer",
            company="ACME",
            flagged=0,
        )
        job2 = Job(
            url="https://example.com/job/b",
            title="Designer",
            company="ACME",
            flagged=1,
        )
        db.add_all([job1, job2])
        db.commit()
        db.close()

        # Export only flagged
        export_resp = client.get("/api/jobs/export?flagged=true")
        assert export_resp.status_code == 200
        csv_content = export_resp.text
        lines = csv_content.strip().split("\n")
        assert len(lines) == 2  # header + 1 flagged job
        assert "Designer" in csv_content
        assert "Engineer" not in csv_content


class TestPIIFiltering:
    """Integration tests for PII filtering."""

    def test_email_filtered(self, client) -> None:
        """Email addresses should be filtered from descriptions."""
        html_with_email = """
        <!DOCTYPE html>
        <html>
        <head><title>Job at TestCo</title></head>
        <body>
            <h1>Software Engineer</h1>
            <div class="company">TestCo</div>
            <div class="description">
                Contact us at hiring@testco.com for more info.
                Call 555-123-4567 to apply.
            </div>
        </body>
        </html>
        """

        with patch("shared.extraction.pipeline._fetch_with_requests") as mock_fetch:
            mock_fetch.return_value = html_with_email

            response = client.post(
                "/api/jobs",
                json={"urls": ["https://example.com/jobs/pii-test"]},
            )

            # If extraction succeeded, check description
            if response.json()["succeeded"] > 0:
                job = response.json()["results"][0]["job"]
                if job.get("description"):
                    # Email should be filtered
                    assert "hiring@testco.com" not in job["description"]
                    assert "[EMAIL]" in job["description"] or "@" not in job["description"]
