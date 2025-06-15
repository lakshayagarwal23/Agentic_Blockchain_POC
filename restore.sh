#!/bin/bash
if [ -z "$1" ]; then
  echo "Usage: ./restore.sh <backup_file>"
  echo "Available backups:"
  ls -la backups/*.tar.gz 2>/dev/null || echo "No backups found"
  exit 1
fi

BACKUP_FILE="$1"
if [ ! -f "$BACKUP_FILE" ]; then
  echo "❌ Backup file not found: $BACKUP_FILE"
  exit 1
fi

echo "⚠  This will restore from backup: $BACKUP_FILE"
echo "⚠  Current data will be backed up first"
read -p "Continue? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Restore cancelled"
  exit 1
fi

echo "💾 Backing up current state..."
./backup.sh

echo "📥 Restoring from backup..."
tar -xzf "$BACKUP_FILE"

echo "✅ Restore completed"
echo "🔄 Please restart the application"
