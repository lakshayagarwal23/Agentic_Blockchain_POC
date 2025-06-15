import sys
import os

# Add the root project path to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.main import app, db  # ✅ this works now!

from sqlalchemy import inspect

try:
    print("🗄 Initializing database...")

    with app.app_context():
        db.drop_all()
        print("📤 Dropped existing tables")

        db.create_all()
        print("📥 Created new tables")

        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"✅ Created tables: {tables}")

    print("🎉 Database initialization complete!")

except Exception as e:
    print(f"❌ Database initialization failed: {e}")
    sys.exit(1)
