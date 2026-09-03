"""
Login module for SUAP authentication.
Handles login flow using Selenium.
"""

import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
)

from src.config import Config

logger = logging.getLogger(__name__)


class SuapLogin:
    """Handles SUAP authentication."""

    def __init__(self, driver):
        self.driver = driver
        self.username = Config.SUAP_USERNAME
        self.password = Config.SUAP_PASSWORD
        self.timeout = Config.TIMEOUT

    def perform_login(self) -> bool:
        """
        Performs login on SUAP.
        Returns True if successful, False otherwise.
        """
        for attempt in range(1, Config.MAX_RETRIES + 1):
            logger.info(f"Login attempt {attempt}/{Config.MAX_RETRIES}")
            try:
                self._navigate_to_login()
                self._fill_credentials()
                self._submit_form()

                if self._is_logged_in():
                    logger.info("Login successful")
                    return True
                else:
                    logger.warning("Login failed - credentials may be incorrect")

            except TimeoutException:
                logger.error(f"Timeout on login attempt {attempt}")
            except Exception as e:
                logger.error(f"Error on login attempt {attempt}: {e}")

            if attempt < Config.MAX_RETRIES:
                logger.info(f"Retrying in 3 seconds...")
                time.sleep(3)

        logger.error("All login attempts failed")
        return False

    def _navigate_to_login(self):
        """Navigate to the SUAP login page."""
        logger.info(f"Navigating to {Config.SUAP_LOGIN_URL}")
        self.driver.get(Config.SUAP_LOGIN_URL)
        time.sleep(3)  # Wait for page to fully render

    def _fill_credentials(self):
        """Fill username and password fields."""
        wait = WebDriverWait(self.driver, self.timeout)

        # Use exact field IDs/names discovered from the page
        # username: id=id_username, name=username
        # password: id=id_password, name=password

        username_field = wait.until(EC.presence_of_element_located((By.ID, "id_username")))
        username_field.clear()
        username_field.send_keys(self.username)
        logger.debug("Username entered")

        password_field = wait.until(EC.presence_of_element_located((By.ID, "id_password")))
        password_field.clear()
        password_field.send_keys(self.password)
        logger.debug("Password entered")

    def _submit_form(self):
        """Submit the login form.

        Na janela de 1920x1080 do modo headless um <ul> da pagina cobre o
        botao "Acessar" e o clique nativo e interceptado. O clique via
        JavaScript nao depende do que esta por cima, entao serve de fallback
        antes de recorrer ao Enter.
        """
        try:
            submit_btn = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Acessar']")
        except NoSuchElementException:
            password_field = self.driver.find_element(By.ID, "id_password")
            password_field.send_keys(Keys.RETURN)
            logger.debug("Submitted form by pressing Enter (no submit button)")
            return

        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
        try:
            submit_btn.click()
            logger.debug("Form submitted via submit button")
        except ElementClickInterceptedException:
            logger.warning("Submit button intercepted; clicking via JavaScript")
            self.driver.execute_script("arguments[0].click();", submit_btn)
            logger.debug("Form submitted via JavaScript click")

    def _is_logged_in(self) -> bool:
        """Check if login was successful."""
        time.sleep(3)  # Wait for redirect

        current_url = self.driver.current_url
        logger.debug(f"Current URL after login: {current_url}")

        # If still on login page, login failed
        if "login" in current_url.lower():
            return False

        # Check for common error messages
        error_indicators = [
            "Usuário ou senha inválidos",
            "Invalid username or password",
            "Credenciais inválidas",
            "authentication-error",
        ]
        page_source = self.driver.page_source.lower()
        for error in error_indicators:
            if error.lower() in page_source:
                return False

        return True
