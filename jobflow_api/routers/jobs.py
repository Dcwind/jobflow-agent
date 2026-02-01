"""Job CRUD and export endpoints."""

import csv
import io
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Response
from shared.db.models import Job
from shared.db.session import get_db
from sqlalchemy.orm import Session

from jobflow_api.config import get_settings
from jobflow_api.dependencies import UserInfo, require_auth, verify_api_key
from jobflow_api.schemas.job import (
    JobCreateRequest,
    JobCreateResponse,
    JobCreateResult,
    JobFlagRequest,
    JobListResponse,
    JobManualCreateRequest,
    JobParseRequest,
    JobParseResponse,
    JobResponse,
    JobUpdateRequest,
)
from jobflow_api.services.scraper import (
    create_manual_job,
    parse_job_from_text,
    scrape_multiple_jobs,
)

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("", response_model=JobCreateResponse, dependencies=[Depends(verify_api_key)])
def create_jobs(
    request: JobCreateRequest,
    user: UserInfo = Depends(require_auth),
    db: Session = Depends(get_db),
) -> JobCreateResponse:
    """Scrape and store jobs from URLs."""
    settings = get_settings()
    results = scrape_multiple_jobs(
        db,
        request.urls,
        user["id"],
        use_playwright=settings.use_playwright,
        use_llm_fallback=settings.use_llm_fallback,
        use_llm_validation=settings.use_llm_validation,
        check_robots=settings.check_robots,
    )

    create_results = []
    for url, job, error in results:
        if job:
            create_results.append(
                JobCreateResult(
                    url=url,
                    success=True,
                    job=JobResponse.model_validate(job),
                )
            )
        else:
            create_results.append(
                JobCreateResult(
                    url=url,
                    success=False,
                    error=error or "Unknown error",
                )
            )

    succeeded = sum(1 for r in create_results if r.success)
    return JobCreateResponse(
        results=create_results,
        total=len(create_results),
        succeeded=succeeded,
        failed=len(create_results) - succeeded,
    )


@router.post("/manual", response_model=JobResponse, dependencies=[Depends(verify_api_key)])
def create_job_manual(
    request: JobManualCreateRequest,
    user: UserInfo = Depends(require_auth),
    db: Session = Depends(get_db),
) -> JobResponse:
    """Create a job from manual entry (for sites that block scraping)."""
    job, error = create_manual_job(
        db,
        request.title,
        request.company,
        user["id"],
        location=request.location,
        salary=request.salary,
        description=request.description,
        url=request.url,
    )
    if error:
        raise HTTPException(status_code=400, detail=error)
    return JobResponse.model_validate(job)


@router.post("/parse", response_model=JobParseResponse, dependencies=[Depends(verify_api_key)])
def parse_job_description(request: JobParseRequest) -> JobParseResponse:
    """Extract job fields from description text using LLM."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")

    fields = parse_job_from_text(request.text)
    return JobParseResponse(**fields)


@router.get("", response_model=JobListResponse)
def list_jobs(
    page: int = 1,
    per_page: int = 20,
    company: str | None = None,
    flagged: bool | None = None,
    user: UserInfo = Depends(require_auth),
    db: Session = Depends(get_db),
) -> JobListResponse:
    """List jobs with pagination and filtering."""
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 20

    query = db.query(Job).filter(Job.user_id == user["id"])

    # Apply filters
    if company:
        query = query.filter(Job.company.ilike(f"%{company}%"))
    if flagged is not None:
        query = query.filter(Job.flagged == (1 if flagged else 0))

    # Get total count
    total = query.count()
    pages = ceil(total / per_page) if total > 0 else 1

    # Paginate
    jobs = query.order_by(Job.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

    return JobListResponse(
        jobs=[JobResponse.model_validate(job) for job in jobs],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


@router.get("/export")
def export_jobs(
    company: str | None = None,
    flagged: bool | None = None,
    user: UserInfo = Depends(require_auth),
    db: Session = Depends(get_db),
) -> Response:
    """Export jobs as CSV."""
    query = db.query(Job).filter(Job.user_id == user["id"])

    if company:
        query = query.filter(Job.company.ilike(f"%{company}%"))
    if flagged is not None:
        query = query.filter(Job.flagged == (1 if flagged else 0))

    jobs = query.order_by(Job.created_at.desc()).all()

    # Build CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["id", "url", "title", "company", "location", "salary", "stage", "description", "created_at"]
    )
    for job in jobs:
        writer.writerow(
            [
                job.id,
                job.url,
                job.title,
                job.company,
                job.location or "",
                job.salary or "",
                job.stage,
                job.description or "",
                job.created_at.isoformat() if job.created_at else "",
            ]
        )

    csv_content = output.getvalue()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=jobs.csv"},
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    user: UserInfo = Depends(require_auth),
    db: Session = Depends(get_db),
) -> JobResponse:
    """Get a single job by ID."""
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user["id"]).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse.model_validate(job)


@router.patch("/{job_id}", response_model=JobResponse, dependencies=[Depends(verify_api_key)])
def update_job(
    job_id: int,
    request: JobUpdateRequest,
    user: UserInfo = Depends(require_auth),
    db: Session = Depends(get_db),
) -> JobResponse:
    """Update job fields (for user corrections)."""
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user["id"]).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)
    return JobResponse.model_validate(job)


@router.patch("/{job_id}/flag", response_model=JobResponse, dependencies=[Depends(verify_api_key)])
def flag_job(
    job_id: int,
    request: JobFlagRequest,
    user: UserInfo = Depends(require_auth),
    db: Session = Depends(get_db),
) -> JobResponse:
    """Flag or unflag a job for review."""
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user["id"]).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.flagged = 1 if request.flagged else 0
    db.commit()
    db.refresh(job)
    return JobResponse.model_validate(job)


@router.delete("/{job_id}", dependencies=[Depends(verify_api_key)])
def delete_job(
    job_id: int,
    user: UserInfo = Depends(require_auth),
    db: Session = Depends(get_db),
) -> dict:
    """Delete a job."""
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user["id"]).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    db.delete(job)
    db.commit()
    return {"deleted": True, "id": job_id}


@router.delete("", dependencies=[Depends(verify_api_key)])
def delete_all_jobs(
    user: UserInfo = Depends(require_auth),
    db: Session = Depends(get_db),
) -> dict:
    """Delete all jobs for the current user (GDPR right to erasure)."""
    count = db.query(Job).filter(Job.user_id == user["id"]).delete()
    db.commit()
    return {"deleted": True, "count": count}
