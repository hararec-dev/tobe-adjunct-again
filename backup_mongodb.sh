#!/bin/bash

# Set variables
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="$HOME/Documents/SOFTWARE/UTILITIES/tobe_adjunct_again/backups"
BACKUP_NAME="mongodb_backup_${TIMESTAMP}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "Starting MongoDB backup to JSON format..."

# Get the list of databases (excluding admin, local, and config)
DATABASES=$(docker exec mongodb mongosh --quiet --username "$MONGO_USERNAME" --password "$MONGO_PASSWORD" --eval "db.adminCommand('listDatabases').databases.map(function(db) { return db.name; }).filter(function(db) { return db !== 'admin' && db !== 'local' && db !== 'config'; }).join(' ')")

# Create a directory for this backup
mkdir -p "$BACKUP_DIR/$BACKUP_NAME"

# Backup each database
for DB in $DATABASES; do
    echo "Backing up database: $DB"
    
    # Get list of collections in the database
    COLLECTIONS=$(docker exec mongodb mongosh --quiet "$DB" --username "$MONGO_USERNAME" --password "$MONGO_PASSWORD" --eval "db.getCollectionNames().join(' ')")
    
    # Create directory for this database
    mkdir -p "$BACKUP_DIR/$BACKUP_NAME/$DB"
    
    # Export each collection to JSON
    for COLLECTION in $COLLECTIONS; do
        echo "Exporting collection: $COLLECTION"
        docker exec mongodb mongoexport \
            --username "$MONGO_USERNAME" \
            --password "$MONGO_PASSWORD" \
            --db "$DB" \
            --collection "$COLLECTION" \
            --out "/tmp/$COLLECTION.json" \
            --jsonArray
        
        # Copy the exported file from the container to the host
        docker cp "mongodb:/tmp/$COLLECTION.json" "$BACKUP_DIR/$BACKUP_NAME/$DB/$COLLECTION.json"
        
        # Remove the temporary file from the container
        docker exec mongodb rm "/tmp/$COLLECTION.json"
    done
done

echo "MongoDB backup completed successfully!"
echo "Backup stored in: $BACKUP_DIR/$BACKUP_NAME"

# Create a compressed archive of the backup
tar -czf "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" -C "$BACKUP_DIR" "$BACKUP_NAME"
echo "Backup compressed to: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"