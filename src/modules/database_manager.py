import logging
from typing import Dict, List

from pymongo import MongoClient

from src.config.settings import MONGO_CONFIG

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self._connect()

    def _connect(self):
        """Establece conexión con MongoDB"""
        try:
            self.client = MongoClient(
                host=MONGO_CONFIG["host"],
                port=MONGO_CONFIG["port"],
                username=MONGO_CONFIG["username"],
                password=MONGO_CONFIG["password"],
            )
            self.db = self.client[MONGO_CONFIG["database"]]
            self.collection = self.db[MONGO_CONFIG["collection"]]
            logger.info("Conexión a MongoDB establecida")
        except Exception as e:
            logger.error(f"Error conectando a MongoDB: {str(e)}")
            raise

    def save_professors(self, professors: List[Dict]):
        """Guarda profesores en la base de datos, actualizando si ya existen"""
        saved_count = 0
        updated_count = 0

        for professor in professors:
            try:
                # Buscar si ya existe por email
                existing = self.collection.find_one({"email": professor["email"]})

                if existing:
                    # Actualizar: combinar las materias
                    existing_subjects = set(existing.get("otherSubjects", []))
                    new_subjects = set(professor.get("otherSubjects", []))

                    # Si la materia actual no está en las otras materias, agregarla
                    current_subject = professor.get("subject")
                    if current_subject and current_subject not in existing_subjects and current_subject != existing.get("subject"):
                        new_subjects.add(current_subject)

                    # Combinar todas las materias
                    all_subjects = existing_subjects.union(new_subjects)

                    # Actualizar el documento
                    self.collection.update_one(
                        {"_id": existing["_id"]},
                        {
                            "$set": {
                                "otherSubjects": list(all_subjects),
                                "isComplexAnalysis": professor.get("isComplexAnalysis", False) or existing.get("isComplexAnalysis", False),
                            }
                        },
                    )
                    updated_count += 1
                    logger.info(f"Actualizado: {professor['name']}")
                else:
                    # Insertar nuevo profesor
                    self.collection.insert_one(professor)
                    saved_count += 1
                    logger.info(f"Guardado: {professor['name']}")

            except Exception as e:
                logger.error(f"Error guardando {professor['name']}: {str(e)}")

        return {"saved": saved_count, "updated": updated_count}

    def close(self):
        """Cierra la conexión a MongoDB"""
        if self.client:
            self.client.close()
