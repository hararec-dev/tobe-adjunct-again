#!/bin/bash

# Create backup directory with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups/$TIMESTAMP"
mkdir -p $BACKUP_DIR

# Run mongodump to create backup
docker exec mongodb mongodump --username=$MONGO_USERNAME --password=$MONGO_PASSWORD --authenticationDatabase=admin --out=/data/db/backup

# Copy from container to host
docker cp mongodb:/data/db/backup $BACKUP_DIR

# Convert BSON to JSON (optional)
echo "Converting BSON to JSON..."
for BSON_FILE in $(find $BACKUP_DIR -name "*.bson"); do
  JSON_FILE="${BSON_FILE%.bson}.json"
  docker exec mongodb bsondump --outFile=$JSON_FILE $BSON_FILE
done

echo "Backup completed at $TIMESTAMP"