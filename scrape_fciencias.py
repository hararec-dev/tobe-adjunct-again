#!/usr/bin/env python3
"""
Script principal para scraping de profesores de la Facultad de Ciencias
"""

import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.modules.database_manager import DatabaseManager
from src.modules.fciencias_scraper import FcienciasScraper

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", handlers=[logging.FileHandler("scraping.log"), logging.StreamHandler(sys.stdout)]
)


def main():
    logger = logging.getLogger(__name__)

    try:
        logger.info("Iniciando scraping de la Facultad de Ciencias...")

        # Inicializar scraper
        scraper = FcienciasScraper(headless=True)

        # Obtener datos de profesores
        logger.info("Obteniendo datos de profesores...")
        professors = scraper.scrape_all_professors()

        logger.info(f"Se obtuvieron datos de {len(professors)} profesores únicos")

        # Guardar en base de datos
        db_manager = DatabaseManager()
        results = db_manager.save_professors(professors)
        db_manager.close()

        logger.info(f"Proceso completado: {results['saved']} nuevos, {results['updated']} actualizados")

        # Mostrar resumen
        for prof in professors[:5]:  # Mostrar primeros 5 como ejemplo
            logger.info(f"Ejemplo: {prof['name']} - {prof['email']} - Materias: {len(prof['otherSubjects']) + 1}")

    except Exception as e:
        logger.error(f"Error en el proceso de scraping: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
