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

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups/$TIMESTAMP"
mkdir -p $BACKUP_DIR
echo "Creando directorio de backup: $BACKUP_DIR"
echo "Exportando $DB_NAME.$COLLECTION_NAME a JSON..."
docker exec mongodb \
  mongoexport \
  --db $DB_NAME \
  --collection $COLLECTION_NAME \
  --username $MONGO_USERNAME \
  --password $MONGO_PASSWORD \
  --authenticationDatabase admin \
  --out /$JSON_FILE \
  --jsonArray

echo "Copiando $JSON_FILE del contenedor al host..."
docker cp mongodb:/$JSON_FILE $BACKUP_DIR/$JSON_FILE
echo "Limpiando archivo temporal en el contenedor..."
docker exec mongodb rm /$JSON_FILE
echo "Backup completado en $BACKUP_DIR/$JSON_FILE"