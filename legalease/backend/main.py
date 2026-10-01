from __future__ import annotations

from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware
)

from backend.config import settings

from backend.routes import router


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "AI-powered legal-document "
        "drafting API for LegalEase."
    )
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=settings.cors_origins,

    allow_credentials=(
        settings.cors_origins != ["*"]
    ),

    allow_methods=["*"],

    allow_headers=["*"],
)


app.include_router(
    router
)


@app.get("/")
def root():

    return {
        "service": settings.app_name,
        "status": "running",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }