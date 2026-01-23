"""Job-related Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl


class JobCreateRequest(BaseModel):
    """Request to create jobs from URLs."""

    urls: list[HttpUrl]


class JobUpdateRequest(BaseModel):
    """Request to update a job."""

    title: str | None = None
    company: str | None = None
    location: str | None = None
    salary: str | None = None
    description: str | None = None


class JobFlagRequest(BaseModel):
    """Request to flag a job for review."""

    flagged: bool


class JobResponse(BaseModel):
    """Single job response."""

    id: int
    url: str
    title: str
    company: str
    location: str | None
    salary: str | None
    description: str | None
    extraction_method: str | None
    flagged: bool
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class JobCreateResult(BaseModel):
    """Result of a single job creation attempt."""

    url: str
    success: bool
    job: JobResponse | None = None
    error: str | None = None


class JobCreateResponse(BaseModel):
    """Response for batch job creation."""

    results: list[JobCreateResult]
    total: int
    succeeded: int
    failed: int


class JobListResponse(BaseModel):
    """Paginated list of jobs."""

    jobs: list[JobResponse]
    total: int
    page: int
    per_page: int
    pages: int
