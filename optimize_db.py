#!/usr/bin/env python3
import sys
sys.path.append('.')

from app.main import app, db
from sqlalchemy import text

def optimize_database():
    print("🔧 Optimizing database...")

    with app.app_context():
        try:
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_assets_user_id ON asset(user_id);",
                "CREATE INDEX IF NOT EXISTS idx_assets_verification_status ON asset(verification_status);",
                "CREATE INDEX IF NOT EXISTS idx_assets_token_id ON asset(token_id);",
                "CREATE INDEX IF NOT EXISTS idx_transactions_asset_id ON transaction(asset_id);",
                "CREATE INDEX IF NOT EXISTS idx_transactions_type ON transaction(transaction_type);",
                "CREATE INDEX IF NOT EXISTS idx_users_wallet ON user(wallet_address);"
            ]

            for index_sql in indexes:
                try:
                    db.session.execute(text(index_sql))
                    print(f"✅ Created index: {index_sql.split('idx_')[1].split(' ')[0]}")
                except Exception as e:
                    print(f"⚠️  Index creation skipped (may already exist): {e}")

            db.session.commit()

            db.session.execute(text("ANALYZE;"))
            db.session.commit()

            print("🎉 Database optimization complete!")

        except Exception as e:
            print(f"❌ Database optimization failed: {e}")
            db.session.rollback()

if __name__ == '__main__':
    optimize_database()
