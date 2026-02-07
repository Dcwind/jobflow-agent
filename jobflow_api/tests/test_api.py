"""Tests for API endpoints."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from shared.db.models import Base, Job
from shared.db.session import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from jobflow_api.dependencies import require_auth
from jobflow_api.main import app

# Test user for mocking authentication
TEST_USER = {"id": "test-user-123", "email": "test@example.com", "name": "Test User"}


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

        def override_require_auth():
            return TEST_USER

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[require_auth] = override_require_auth
        yield TestingSessionLocal
        app.dependency_overrides.clear()


@pytest.fixture
def client(test_db):
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def sample_job(test_db):
    """Create a sample job in the database."""
    db = test_db()
    job = Job(
        url="https://example.com/job/123",
        user_id=TEST_USER["id"],
        title="Software Engineer",
        company="ACME Corp",
        location="San Francisco, CA",
        salary="$150,000 - $200,000",
        description="Build amazing software.",
        extraction_method="bs4",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    job_id = job.id
    db.close()
    return job_id


class TestHealthEndpoints:
    """Tests for health endpoints."""

    def test_health_check(self, client) -> None:
        """Health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root(self, client) -> None:
        """Root endpoint returns service info."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["service"] == "Jobflow API"


class TestJobsListEndpoint:
    """Tests for listing jobs."""

    def test_list_jobs_empty(self, client) -> None:
        """List returns empty when no jobs exist."""
        response = client.get("/api/jobs")
        assert response.status_code == 200
        data = response.json()
        assert data["jobs"] == []
        assert data["total"] == 0

    def test_list_jobs_with_data(self, client, sample_job) -> None:
        """List returns jobs when they exist."""
        response = client.get("/api/jobs")
        assert response.status_code == 200
        data = response.json()
        assert len(data["jobs"]) == 1
        assert data["jobs"][0]["title"] == "Software Engineer"

    def test_list_jobs_pagination(self, client, test_db) -> None:
        """Pagination works correctly."""
        # Create 5 jobs
        db = test_db()
        for i in range(5):
            job = Job(
                url=f"https://example.com/job/{i}",
                user_id=TEST_USER["id"],
                title=f"Job {i}",
                company="ACME",
            )
            db.add(job)
        db.commit()
        db.close()

        response = client.get("/api/jobs?per_page=2&page=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["jobs"]) == 2
        assert data["total"] == 5
        assert data["pages"] == 3


class TestJobsGetEndpoint:
    """Tests for getting a single job."""

    def test_get_job(self, client, sample_job) -> None:
        """Get returns the job."""
        response = client.get(f"/api/jobs/{sample_job}")
        assert response.status_code == 200
        assert response.json()["title"] == "Software Engineer"

    def test_get_job_not_found(self, client) -> None:
        """Get returns 404 for non-existent job."""
        response = client.get("/api/jobs/99999")
        assert response.status_code == 404


class TestJobsUpdateEndpoint:
    """Tests for updating jobs."""

    def test_update_job(self, client, sample_job) -> None:
        """Update modifies job fields."""
        response = client.patch(
            f"/api/jobs/{sample_job}",
            json={"title": "Senior Engineer", "location": "Remote"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Senior Engineer"
        assert data["location"] == "Remote"
        assert data["company"] == "ACME Corp"  # unchanged

    def test_update_job_not_found(self, client) -> None:
        """Update returns 404 for non-existent job."""
        response = client.patch("/api/jobs/99999", json={"title": "New Title"})
        assert response.status_code == 404


class TestJobsFlagEndpoint:
    """Tests for flagging jobs."""

    def test_flag_job(self, client, sample_job) -> None:
        """Flag sets the flagged status."""
        response = client.patch(f"/api/jobs/{sample_job}/flag", json={"flagged": True})
        assert response.status_code == 200
        assert response.json()["flagged"] is True

    def test_unflag_job(self, client, sample_job, test_db) -> None:
        """Unflag clears the flagged status."""
        # First flag it
        db = test_db()
        job = db.query(Job).filter(Job.id == sample_job).first()
        job.flagged = 1
        db.commit()
        db.close()

        response = client.patch(f"/api/jobs/{sample_job}/flag", json={"flagged": False})
        assert response.status_code == 200
        assert response.json()["flagged"] is False


class TestJobsDeleteEndpoint:
    """Tests for deleting jobs."""

    def test_delete_job(self, client, sample_job) -> None:
        """Delete removes the job."""
        response = client.delete(f"/api/jobs/{sample_job}")
        assert response.status_code == 200
        assert response.json()["deleted"] is True

        # Verify it's gone
        response = client.get(f"/api/jobs/{sample_job}")
        assert response.status_code == 404

    def test_delete_job_not_found(self, client) -> None:
        """Delete returns 404 for non-existent job."""
        response = client.delete("/api/jobs/99999")
        assert response.status_code == 404


class TestJobsExportEndpoint:
    """Tests for exporting jobs."""

    def test_export_csv(self, client, sample_job) -> None:
        """Export returns CSV."""
        response = client.get("/api/jobs/export")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "Software Engineer" in response.text
        assert "ACME Corp" in response.text

    def test_export_csv_empty(self, client) -> None:
        """Export returns CSV header even when empty."""
        response = client.get("/api/jobs/export")
        assert response.status_code == 200
        assert "id,url,title,company" in response.text


class TestJobsCreateEndpoint:
    """Tests for creating jobs (mocked extraction)."""

    def test_create_job_mock(self, client, test_db) -> None:
        """Create with mocked extraction."""
        from shared.extraction.bs4_extractor import ExtractionResult
        from shared.extraction.pipeline import ExtractionMetrics

        mock_result = ExtractionResult(
            title="Backend Developer",
            company="Test Inc",
            location="NYC",
            salary="$100k",
            description="Test job",
            source="bs4",
        )
        mock_metrics = ExtractionMetrics(
            fetch_method="requests",
            extraction_method="bs4",
            validation_run=False,
            confidence=0.8,
            fallbacks_used=0,
        )

        with patch(
            "jobflow_api.services.scraper.extract_job",
            return_value=(mock_result, mock_metrics),
        ):
            response = client.post(
                "/api/jobs",
                json={"urls": ["https://example.com/job/new"]},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["succeeded"] == 1
            assert data["failed"] == 0
            assert data["results"][0]["job"]["title"] == "Backend Developer"


class TestJobsStageEndpoint:
    """Tests for job stage functionality."""

    def test_default_stage_is_backlog(self, client, sample_job) -> None:
        """New jobs have stage = Backlog by default."""
        response = client.get(f"/api/jobs/{sample_job}")
        assert response.status_code == 200
        assert response.json()["stage"] == "Backlog"

    def test_update_stage(self, client, sample_job) -> None:
        """Stage can be updated via PATCH."""
        response = client.patch(
            f"/api/jobs/{sample_job}",
            json={"stage": "Applied"},
        )
        assert response.status_code == 200
        assert response.json()["stage"] == "Applied"

        # Verify it persists
        response = client.get(f"/api/jobs/{sample_job}")
        assert response.json()["stage"] == "Applied"

    def test_stage_in_csv_export(self, client, sample_job, test_db) -> None:
        """Stage is included in CSV export."""
        # Set a specific stage
        db = test_db()
        job = db.query(Job).filter(Job.id == sample_job).first()
        job.stage = "Interviewing"
        db.commit()
        db.close()

        response = client.get("/api/jobs/export")
        assert response.status_code == 200
        assert "stage" in response.text
        assert "Interviewing" in response.text
