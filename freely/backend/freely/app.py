"""FastAPI application factory."""

import contextlib
from collections.abc import AsyncIterator
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from freely import kit
from freely.config import settings

# Will be populated later
from freely import api  # noqa: F401


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[dict[str, Any]]:
    """
    Application lifespan manager.

    Runs on startup and shutdown.
    """
    # Startup
    engine = kit.db.create_engine()
    sessionmaker = kit.db.create_sessionmaker(engine)

    # Store in app state (for middleware)
    state = {
        "engine": engine,
        "sessionmaker": sessionmaker,
    }

    # Store globally for easy access
    global _engine, _sessionmaker
    kit.db._engine = engine
    kit.db._sessionmaker = sessionmaker

    yield state

    # Shutdown
    await engine.dispose()


class AsyncSessionMiddleware(BaseHTTPMiddleware):
    """
    Middleware that provides database session for each request.

    Session is automatically committed on success, rolled back on error.
    """

    async def dispatch(self, request: Request, call_next):
        sessionmaker = request.app.state.sessionmaker

        async with sessionmaker() as session:
            # Store in request state
            request.state.db_session = session

            try:
                response = await call_next(request)
                await session.commit()
                return response
            except Exception:
                await session.rollback()
                raise


def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="Freely API",
        description="Global commerce platform with AI agents",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
    )

    # Middleware (order matters - bottom executes first)
    configure_cors(app)
    app.add_middleware(AsyncSessionMiddleware)

    # Exception handlers
    add_exception_handlers(app)

    # Routes
    app.include_router(api.router)

    # Health check
    @app.get("/healthz")
    async def health_check():
        return {"status": "ok"}

    return app


def configure_cors(app: FastAPI) -> None:
    """Configure CORS middleware."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def add_exception_handlers(app: FastAPI) -> None:
    """Add global exception handlers."""

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Handle uncaught exceptions."""
        if settings.is_development:
            # In development, show full traceback
            raise exc

        # In production, hide internal errors
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )


# Create app instance
app = create_app()
