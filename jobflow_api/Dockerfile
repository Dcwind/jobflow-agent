FROM python:3.11-slim

WORKDIR /app

# Install uv for fast dependency management
RUN pip install uv

# Copy shared package first
COPY shared/ ./shared/

# Copy API package
COPY jobflow_api/ ./jobflow_api/

# Create data directory for SQLite
RUN mkdir -p ./data

# Install dependencies
RUN uv pip install --system ./shared ./jobflow_api

# Expose port
EXPOSE 8000

# Run the app
CMD ["uvicorn", "jobflow_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
