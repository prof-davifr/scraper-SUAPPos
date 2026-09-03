"""
Scraper module for extracting student data from SUAP.
Uses the built-in XLS export via the task system.
"""

import logging
import os
import time
import re
import io

from src.config import Config

logger = logging.getLogger(__name__)


class AlunosScraper:
    """Downloads aluno data from SUAP using the XLS export task system."""

    def __init__(self, driver):
        self.driver = driver
        self.timeout = Config.TIMEOUT

    def scrape_all(self, modalidades: list[int] | None = None) -> list[dict]:
        """
        Scrapes student data for all specified modalidades using XLS export.
        Returns a list of student dictionaries.

        Nenhum filtro por nome de curso: a modalidade 10 do SUAP já é a
        Especialização, e todo curso dela é pós-graduação lato sensu.

        Havia um filtro aqui, `_is_lato_sensu()`, que mantinha só os cursos cujo
        nome trazia a expressão "lato sensu". Ele descartava 2193 alunos em 45
        cursos chamados apenas "Especialização em ...". O painel mostrava 573
        especializandos contra os 2766 do SUAP, e 13 campi sumiam da aba de
        Pós-Graduação. Removido em setembro de 2026.
        """
        if modalidades is None:
            modalidades = [
                Config.MODALIDADE_MESTRADO,
                Config.MODALIDADE_ESPECIALIZACAO,
                Config.MODALIDADE_DOUTORADO,
            ]

        all_students = []

        for modalidade_id in modalidades:
            modalidade_name = self._get_modalidade_name(modalidade_id)

            logger.info(f"Exporting {modalidade_name} (id={modalidade_id})")
            url = Config.get_alunos_url_filtered(modalidade_id)

            self.driver.get(url)
            time.sleep(5)

            # Check if we need to re-authenticate
            if "login" in self.driver.current_url.lower():
                logger.warning("Session expired, need to re-authenticate")
                break

            students = self._export_and_parse()

            logger.info(f"Exported {len(students)} students for {modalidade_name}")

            for student in students:
                student["modalidade"] = modalidade_name

            all_students.extend(students)

        return all_students

    @staticmethod
    def _get_modalidade_name(modalidade_id: int) -> str:
        """Returns the name for a modalidade ID."""
        if modalidade_id == Config.MODALIDADE_MESTRADO:
            return "Mestrado"
        elif modalidade_id == Config.MODALIDADE_DOUTORADO:
            return "Doutorado"
        elif modalidade_id == Config.MODALIDADE_ESPECIALIZACAO:
            return "Especialização"
        return f"Modalidade {modalidade_id}"

    def _export_and_parse(self) -> list[dict]:
        """Triggers the XLS export via Selenium, follows the task, and downloads the file."""
        try:
            import pandas as pd
            import requests
            from selenium.webdriver.common.by import By

            # Click the export link to trigger the task
            export_link = self.driver.find_element(By.CSS_SELECTOR, "a[href*='export_to_xls']")
            export_link.click()

            # Wait for task page and poll for completion
            task_id = self._wait_for_task_completion()
            if not task_id:
                logger.error("Task did not complete")
                return []

            # Download the XLS file using the task download endpoint
            download_url = f"{Config.SUAP_BASE_URL}/djtools/process_progress2/1/{task_id}/"
            logger.info(f"Download URL: {download_url}")

            # Use requests with Selenium cookies
            session = requests.Session()
            for cookie in self.driver.get_cookies():
                session.cookies.set(
                    cookie["name"],
                    cookie["value"],
                    domain=cookie.get("domain"),
                    path=cookie.get("path"),
                )

            user_agent = self.driver.execute_script("return navigator.userAgent;")
            session.headers.update({
                "User-Agent": user_agent,
                "Referer": f"{Config.SUAP_BASE_URL}/djtools/process2/{task_id}/",
            })

            response = session.get(download_url, timeout=120, allow_redirects=True)
            logger.info(f"Download: status={response.status_code}, size={len(response.content)} bytes")

            if len(response.content) < 100:
                logger.error(f"Downloaded content too small, likely not an XLS file")
                return []

            # Save for reference
            os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
            filepath = os.path.join(Config.OUTPUT_DIR, f"raw_export_{int(time.time())}.xls")
            with open(filepath, "wb") as f:
                f.write(response.content)
            logger.info(f"Saved XLS to {filepath}")

            # Parse the XLS file - row 0 contains the header names
            try:
                df = pd.read_excel(io.BytesIO(response.content), engine="xlrd", header=1)
            except Exception:
                df = pd.read_excel(io.BytesIO(response.content), engine="openpyxl", header=1)

            logger.info(f"DataFrame shape: {df.shape}, columns: {list(df.columns)[:10]}...")

            # Drop rows where all values are NaN
            df = df.dropna(how="all")

            # Convert to list of dicts with cleaned keys
            students = []
            for _, row in df.iterrows():
                student = {}
                for key, value in row.items():
                    clean_key = str(key).strip().lower().replace(" ", "_")
                    if pd.isna(value):
                        student[clean_key] = None
                    else:
                        student[clean_key] = value
                students.append(student)

            return students

        except ImportError:
            logger.error("pandas or requests not installed")
            return []
        except Exception as e:
            logger.error(f"Error in export: {e}", exc_info=True)
            return []

    def _wait_for_task_completion(self) -> str | None:
        """
        Waits for the export task to complete by polling the task page.
        Returns the task ID when complete, or None on failure.
        """
        from selenium.webdriver.common.by import By

        max_wait = 120  # seconds
        start = time.time()

        while time.time() - start < max_wait:
            time.sleep(3)

            # Extract task ID from URL: /djtools/process2/<task_id>/
            current_url = self.driver.current_url
            match = re.search(r"/process2/(\d+)/", current_url)
            if not match:
                continue

            task_id = match.group(1)

            # Check if task is complete
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            if "Arquivo gerado com sucesso" in body_text:
                logger.info(f"Task {task_id} completed")
                return task_id

            if "processada" in body_text.lower() or "aguarde" in body_text.lower():
                logger.debug(f"Task {task_id} still processing... ({int(time.time()-start)}s)")
                continue

            # Check page source for completion via JS (100%)
            source = self.driver.page_source
            if "100" in source and "Arquivo gerado" in source:
                logger.info(f"Task {task_id} completed (detected via source)")
                return task_id

        logger.error(f"Task timed out after {max_wait}s")
        return None
