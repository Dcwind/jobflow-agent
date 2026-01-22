"""Tests for database models."""

import tempfile
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shared.db.models import Base, Job


@pytest.fixture
def db_session():
    """Create a test database session."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()


class TestJobModel:
    """Tests for Job model."""

    def test_create_job(self, db_session) -> None:
        """Create a job record."""
        job = Job(
            url="https://example.com/job/123",
            title="Software Engineer",
            company="ACME Corp",
            location="San Francisco, CA",
            salary="$150,000 - $200,000",
            description="We are looking for a talented engineer.",
            extraction_method="bs4",
        )
        db_session.add(job)
        db_session.commit()

        assert job.id is not None
        assert job.created_at is not None

    def test_unique_url(self, db_session) -> None:
        """URL must be unique."""
        job1 = Job(
            url="https://example.com/job/123",
            title="Engineer",
            company="ACME",
        )
        job2 = Job(
            url="https://example.com/job/123",
            title="Designer",
            company="ACME",
        )
        db_session.add(job1)
        db_session.commit()

        db_session.add(job2)
        with pytest.raises(Exception):  # noqa: B017 - IntegrityError
            db_session.commit()

    def test_to_dict(self, db_session) -> None:
        """Convert job to dictionary."""
        job = Job(
            url="https://example.com/job/123",
            title="Engineer",
            company="ACME",
            location="NYC",
            flagged=1,
        )
        db_session.add(job)
        db_session.commit()

        d = job.to_dict()
        assert d["url"] == "https://example.com/job/123"
        assert d["title"] == "Engineer"
        assert d["flagged"] is True
        assert "created_at" in d

    def test_query_by_company(self, db_session) -> None:
        """Query jobs by company."""
        jobs = [
            Job(url=f"https://example.com/job/{i}", title="Engineer", company="ACME")
            for i in range(3)
        ]
        jobs.append(Job(url="https://example.com/job/other", title="Designer", company="Other"))
        db_session.add_all(jobs)
        db_session.commit()

        acme_jobs = db_session.query(Job).filter(Job.company == "ACME").all()
        assert len(acme_jobs) == 3
