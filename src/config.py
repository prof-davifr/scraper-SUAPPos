"""
Configuration module for the SUAPPos scraper.
Loads environment variables and provides constants.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Centralized configuration for the scraper."""

    # SUAP credentials
    SUAP_USERNAME = os.getenv("SUAP_USERNAME", "")
    SUAP_PASSWORD = os.getenv("SUAP_PASSWORD", "")

    # SUAP URLs
    SUAP_BASE_URL = os.getenv("SUAP_BASE_URL", "https://suap.ifba.edu.br")
    SUAP_LOGIN_URL = f"{SUAP_BASE_URL}/accounts/login/?next=/"
    SUAP_ALUNOS_URL = f"{SUAP_BASE_URL}/admin/edu/aluno/"

    # Output settings
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")
    OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", "csv").lower()

    # Browser settings
    HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
    TIMEOUT = int(os.getenv("TIMEOUT", "30"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

    # Filters for pos-graduacao
    MODALIDADE_MESTRADO = 9
    MODALIDADE_ESPECIALIZACAO = 10
    MODALIDADE_DOUTORADO = 16

    @classmethod
    def get_alunos_url_filtered(cls, modalidade_id: int | None = None) -> str:
        """Returns the alunos URL with filters applied."""
        url = cls.SUAP_ALUNOS_URL
        if modalidade_id is not None:
            url += f"?curso_campus__modalidade__id__exact={modalidade_id}&tab=tab_any_data"
        return url

    @classmethod
    def validate(cls) -> list[str]:
        """Validates required configuration. Returns list of errors."""
        errors = []
        if not cls.SUAP_USERNAME:
            errors.append("SUAP_USERNAME is required")
        if not cls.SUAP_PASSWORD:
            errors.append("SUAP_PASSWORD is required")
        if cls.OUTPUT_FORMAT not in ("csv", "json", "xlsx"):
            errors.append(f"Invalid OUTPUT_FORMAT: {cls.OUTPUT_FORMAT}")
        return errors
