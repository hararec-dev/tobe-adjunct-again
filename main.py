import argparse
import logging

from src.core.notification.use_cases import send_emails
from src.core.scraping.use_cases import scrape_professors

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main():
    parser = argparse.ArgumentParser(description="Sistema de envío de emails a profesores")
    parser.add_argument("--scrape", action="store_true", help="Ejecutar scraping antes de enviar emails")
    parser.add_argument("--scrape-only", action="store_true", help="Solo ejecutar scraping, no enviar emails")

    args = parser.parse_args()

    if args.scrape or args.scrape_only:
        scrape_professors()

    if not args.scrape_only:
        send_emails()


if __name__ == "__main__":
    main()
