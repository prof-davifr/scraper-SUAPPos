"""
Exporter module for saving extracted student data to files.
Supports CSV, JSON, and Excel formats.
"""

import logging
import os
import json
from datetime import datetime

import pandas as pd

from src.config import Config

logger = logging.getLogger(__name__)


class DataExporter:
    """Exports scraped student data to various formats."""

    def __init__(self, output_dir: str | None = None):
        self.output_dir = output_dir or Config.OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def export(self, data: list[dict], fmt: str | None = None) -> str:
        """
        Exports data to the specified format.
        Returns the path to the exported file.
        """
        if fmt is None:
            fmt = Config.OUTPUT_FORMAT

        if not data:
            logger.warning("No data to export")
            return ""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if fmt == "csv":
            filepath = os.path.join(self.output_dir, f"alunos_pos_{timestamp}.csv")
            self._export_csv(data, filepath)
        elif fmt == "json":
            filepath = os.path.join(self.output_dir, f"alunos_pos_{timestamp}.json")
            self._export_json(data, filepath)
        elif fmt == "xlsx":
            filepath = os.path.join(self.output_dir, f"alunos_pos_{timestamp}.xlsx")
            self._export_excel(data, filepath)
        else:
            raise ValueError(f"Unsupported format: {fmt}")

        logger.info(f"Data exported to {filepath}")
        return filepath

    def _export_csv(self, data: list[dict], filepath: str):
        """Exports data to CSV format."""
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        logger.info(f"Exported {len(data)} records to CSV")

    def _export_json(self, data: list[dict], filepath: str):
        """Exports data to JSON format."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Exported {len(data)} records to JSON")

    def _export_excel(self, data: list[dict], filepath: str):
        """Exports data to Excel format."""
        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False, engine="openpyxl")
        logger.info(f"Exported {len(data)} records to Excel")
