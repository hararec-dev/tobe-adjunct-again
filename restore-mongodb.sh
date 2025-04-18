#!/bin/bash

# Check if backup directory is provided
if [ -z "$1" ]; then
  echo "Please provide the backup directory timestamp"
  echo "Usage: ./restore-mongodb.sh 20230815_120000"
  
  echo "Available backups:"
  ls -la ./backups
  exit 1
fi

BACKUP_DIR="./backups/$1"

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
  echo "Backup directory $BACKUP_DIR does not exist"
  echo "Available backups:"
  ls -la ./backups
  exit 1
fi

# Copy backup to container
echo "Copying backup to container..."
docker exec -it mongodb rm -rf /tmp/backup || true
docker cp $BACKUP_DIR mongodb:/tmp/backup

# Restore backup
echo "Restoring backup..."
docker exec -it mongodb mongorestore --username=$MONGO_USERNAME --password=$MONGO_PASSWORD --authenticationDatabase=admin /tmp/backup

echo "Backup restored successfully!"