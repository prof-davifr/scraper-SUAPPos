"""
Main entry point for the SUAPPos scraper.
Orchestrates login, scraping, and data export.
"""

import argparse
import logging
import sys
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from src.config import Config
from src.login import SuapLogin
from src.scraper import AlunosScraper
from src.exporter import DataExporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scraper.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def setup_driver(headless: bool = False) -> webdriver.Chrome:
    """Sets up the Chrome WebDriver."""
    chrome_options = Options()

    if headless:
        chrome_options.add_argument("--headless=new")

    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    # Prefer undetected chromedriver if available
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except ImportError:
        driver = webdriver.Chrome(options=chrome_options)

    return driver


def parse_args():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="SUAPPos Scraper - Extract post-grad student data from SUAP/IFBA")
    parser.add_argument(
        "--format",
        choices=["csv", "json", "xlsx"],
        default=None,
        help="Output format (overrides .env config)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=None,
        help="Run browser in headless mode",
    )
    parser.add_argument(
        "--modalidade",
        choices=["mestrado", "doutorado", "especializacao", "both"],
        default="both",
        help="Which post-grad level to scrape (default: both = all three)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Custom output directory",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Set debug level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate config
    errors = Config.validate()
    if errors:
        logger.error(f"Configuration errors: {errors}")
        logger.error("Please check your .env file")
        sys.exit(1)

    # Resolve settings from args
    headless = args.headless if args.headless is not None else Config.HEADLESS
    output_format = args.format if args.format else Config.OUTPUT_FORMAT
    output_dir = args.output_dir if args.output_dir else Config.OUTPUT_DIR

    # Determine modalidades
    if args.modalidade == "mestrado":
        modalidades = [Config.MODALIDADE_MESTRADO]
    elif args.modalidade == "doutorado":
        modalidades = [Config.MODALIDADE_DOUTORADO]
    elif args.modalidade == "especializacao":
        modalidades = [Config.MODALIDADE_ESPECIALIZACAO]
    else:
        modalidades = None  # All three

    driver = None
    try:
        # Setup browser
        logger.info("Starting browser...")
        driver = setup_driver(headless=headless)
        driver.implicitly_wait(5)

        # Login
        logger.info("Authenticating on SUAP...")
        login_handler = SuapLogin(driver)
        if not login_handler.perform_login():
            logger.error("Failed to login to SUAP")
            sys.exit(1)

        # Scrape
        logger.info("Starting data extraction...")
        scraper = AlunosScraper(driver)
        students = scraper.scrape_all(modalidades=modalidades)

        if not students:
            logger.warning("No students found. Check credentials and page structure.")
            sys.exit(1)

        logger.info(f"Total students extracted: {len(students)}")

        # Export
        logger.info(f"Exporting data in {output_format} format...")
        exporter = DataExporter(output_dir=output_dir)
        filepath = exporter.export(students, fmt=output_format)

        if filepath:
            logger.info(f"✅ Data saved to: {filepath}")
            # Print summary
            print(f"\n{'='*60}")
            print(f"SCRAPING COMPLETE")
            print(f"Total records: {len(students)}")
            print(f"Output file: {filepath}")
            print(f"{'='*60}")

            # Print column preview
            if students:
                print(f"\nAvailable fields: {', '.join(students[0].keys())}")
                print(f"\nFirst record preview:")
                for key, value in list(students[0].items()):
                    print(f"  {key}: {str(value)[:80]}{'...' if len(str(value)) > 80 else ''}")

        else:
            logger.warning("Export returned no file path")

    except KeyboardInterrupt:
        logger.info("Scraper interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if driver:
            logger.info("Closing browser...")
            driver.quit()


if __name__ == "__main__":
    main()
