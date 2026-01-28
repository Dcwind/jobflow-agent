"""FastAPI application entry point."""

# Load .env into os.environ before any other imports
from dotenv import load_dotenv

load_dotenv()

import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from shared.db.session import init_db
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from jobflow_api.config import get_settings
from jobflow_api.routers import health, jobs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting Jobflow API...")
    init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down Jobflow API...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        lifespan=lifespan,
    )

    # Rate limiting
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request ID middleware
    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        logger.info("Request %s: %s %s", request_id, request.method, request.url.path)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    # Include routers
    app.include_router(health.router)
    app.include_router(jobs.router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("jobflow_api.main:app", host="0.0.0.0", port=8000, reload=True)
