# Multi-stage build for production
FROM python:3.12-slim as builder

# Install uv
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Runtime stage
FROM python:3.12-slim

# Create non-root user
RUN useradd -m -u 1000 freely

# Set working directory
WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY freely ./freely
COPY alembic.ini ./

# Set ownership
RUN chown -R freely:freely /app

# Switch to non-root user
USER freely

# Set environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "freely.app:app", "--host", "0.0.0.0", "--port", "8000"]
