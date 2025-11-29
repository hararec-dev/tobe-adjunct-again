#!/usr/bin/env python3

import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decouple import config

from src.modules.database_manager import DatabaseManager
from src.modules.fciencias_scraper import FcienciasScraper

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", handlers=[logging.FileHandler("scraping.log"), logging.StreamHandler(sys.stdout)]
)


def main():
    logger = logging.getLogger(__name__)

    try:
        logger.info("Iniciando scraping de la Facultad de Ciencias...")

        # Inicializar scraper
        scraper = FcienciasScraper(headless=not config("OPEN_BROWSER", default=False, cast=bool))

        # Obtener datos de profesores - MODO PRUEBA con 2 asignaturas
        logger.info("Obteniendo datos de profesores...")
        professors = scraper.scrape_all_professors(max_subjects=2)

        if not professors:
            logger.error("No se obtuvieron datos de profesores")
            sys.exit(1)

        logger.info(f"Se obtuvieron datos de {len(professors)} profesores únicos")

        # Guardar en base de datos
        db_manager = DatabaseManager()
        results = db_manager.save_professors(professors)
        db_manager.close()

        logger.info(f"Proceso completado: {results['saved']} nuevos, {results['updated']} actualizados")

        # Mostrar resumen detallado
        logger.info("=== RESUMEN DE PROFESORES OBTENIDOS ===")
        for i, prof in enumerate(professors, 1):
            logger.info(f"{i}. {prof['name']} - {prof['email']}")
            logger.info(f"   Materia principal: {prof['subject']}")
            logger.info(f"   Otras materias: {len(prof['otherSubjects'])}")
            if prof["otherSubjects"]:
                logger.info(f"   -> {', '.join(prof['otherSubjects'][:3])}")
                if len(prof["otherSubjects"]) > 3:
                    logger.info(f"   -> ... y {len(prof['otherSubjects']) - 3} más")
            logger.info("")

    except Exception as e:
        logger.error(f"Error en el proceso de scraping: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
