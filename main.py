import argparse
import logging
import time

from pymongo import MongoClient

from src.config.settings import MONGO_CONFIG
from src.modules.database_manager import DatabaseManager
from src.modules.email_sender import EmailSender
from src.modules.fciencias_scraper import FcienciasScraper

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def scrape_professors():
    """Ejecuta el scraping y guarda en la base de datos"""
    logging.info("Iniciando scraping de profesores...")

    scraper = FcienciasScraper(headless=True)
    professors = scraper.scrape_all_professors()

    db_manager = DatabaseManager()
    results = db_manager.save_professors(professors)
    db_manager.close()

    logging.info(f"Scraping completado: {results['saved']} nuevos, {results['updated']} actualizados")
    return results


def send_emails():
    """Envía emails a profesores (función original)"""
    email_sender = EmailSender()
    client = MongoClient(
        host=MONGO_CONFIG["host"],
        port=MONGO_CONFIG["port"],
        username=MONGO_CONFIG["username"],
        password=MONGO_CONFIG["password"],
    )

    db = client[MONGO_CONFIG["database"]]
    collection = db[MONGO_CONFIG["collection"]]
    teachers = list(collection.find({"wasEmailSend": False}))
    start_time = time.time()

    try:
        email_sender.connect()
        sent_count = 0

        for teacher in teachers:
            try:
                email_sender.send_email(teacher, use_existing_connection=True)
                collection.update_one({"_id": teacher["_id"]}, {"$set": {"wasEmailSend": True}})
                print(f"Email enviado a {teacher['email']}")
                sent_count += 1
            except Exception as e:
                print(f"Error enviando a {teacher['email']}: {str(e)}")
    finally:
        email_sender.disconnect()
        client.close()
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"\nSe enviaron {sent_count} emails en {execution_time:.2f} segundos")


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
