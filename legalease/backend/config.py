from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_ROOT / ".env")


class Settings:
    app_name = "LegalEase"
    app_version = "1.0.0"

    gemini_api_key = os.getenv(
        "GEMINI_API_KEY",
        ""
    ).strip()

    gemini_model = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.8-flash"
    ).strip()

    backend_host = os.getenv(
        "BACKEND_HOST",
        "127.0.0.1"
    )

    backend_port = int(
        os.getenv(
            "BACKEND_PORT",
            "8000"
        )
    )

    backend_url = os.getenv(
        "BACKEND_URL",
        "http://127.0.0.1:8000"
    ).rstrip("/")

    cors_origins_raw = os.getenv(
        "CORS_ORIGINS",
        "*"
    )

    @property
    def cors_origins(self) -> list[str]:

        if self.cors_origins_raw.strip() == "*":
            return ["*"]

        return [
            origin.strip()
            for origin in self.cors_origins_raw.split(",")
            if origin.strip()
        ]


settings = Settings()