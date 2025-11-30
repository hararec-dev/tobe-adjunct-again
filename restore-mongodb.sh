#!/bin/bash

ENV_FILE=".env"
if [ -f "$ENV_FILE" ]; then
    echo "Cargando variables desde $ENV_FILE"
    source "$ENV_FILE"
fi

if [ -z "$MONGO_USERNAME" ] || [ -z "$MONGO_PASSWORD" ]; then
  echo "Error: Las variables MONGO_USERNAME y MONGO_PASSWORD deben estar definidas."
  exit 1
fi

DB_NAME="teachers"
COLLECTION_NAME="development"
JSON_FILE="$COLLECTION_NAME.json"
if [ -z "$1" ]; then
  echo "Por favor, proporciona el timestamp del directorio de backup."
  echo "Uso: ./restore-mongodb.sh 20230815_120000"
  echo "Backups disponibles:"
  ls -la ./backups
  exit 1
fi

BACKUP_DIR="./backups/$1"
if [ ! -d "$BACKUP_DIR" ]; then
  echo "El directorio de backup $BACKUP_DIR no existe."
  echo "Backups disponibles:"
  ls -la ./backups
  exit 1
fi

if [ ! -f "$BACKUP_DIR/$JSON_FILE" ]; then
  echo "El archivo de datos $JSON_FILE no se encontró en $BACKUP_DIR."
  exit 1
fi

echo "Copiando backup JSON ($JSON_FILE) al contenedor..."
docker cp $BACKUP_DIR/$JSON_FILE mongodb:/tmp/$JSON_FILE
echo "Restaurando $DB_NAME.$COLLECTION_NAME desde /tmp/$JSON_FILE..."
docker exec -it mongodb \
  mongoimport \
  --db $DB_NAME \
  --collection $COLLECTION_NAME \
  --username $MONGO_USERNAME \
  --password $MONGO_PASSWORD \
  --authenticationDatabase admin \
  --file /tmp/$JSON_FILE \
  --jsonArray \
  --drop

echo "Limpiando archivo temporal en el contenedor..."
docker exec mongodb rm /tmp/$JSON_FILE || true
echo "Backup restaurado exitosamente en $DB_NAME.$COLLECTION_NAME!"