import logging

from src.core.persistance.repository import ProfessorRepository
from src.core.scraping.services import FcienciasScraper


def scrape_professors():
    """Ejecuta el scraping y guarda en la base de datos"""
    logging.info("Iniciando scraping de profesores...")

    scraper = FcienciasScraper(headless=True)
    professors = scraper.scrape_all_professors()

    db_manager = ProfessorRepository()
    results = db_manager.save_professors(professors)
    db_manager.close()

    logging.info(f"Scraping completado: {results['saved']} nuevos, {results['updated']} actualizados")
    return results
