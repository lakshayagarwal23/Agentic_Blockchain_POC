#!/bin/bash
BACKUP_DIR="backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="rwa_backup_$DATE"

echo "💾 Creating backup: $BACKUP_NAME"
mkdir -p "$BACKUP_DIR"

tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='logs/*.log' \
  --exclude='backups' \
  .

echo "✅ Backup created: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
cd "$BACKUP_DIR"
ls -t *.tar.gz | tail -n +6 | xargs -r rm --
echo "🧹 Old backups cleaned up"

echo "📊 Backup Information:"
echo "  File: $BACKUP_NAME.tar.gz"
echo "  Size: $(du -h $BACKUP_NAME.tar.gz | cut -f1)"
echo "  Date: $(date)"
