"""Bootstrap script to seed initial data."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.database import SessionLocal, engine, Base
from app.main import _bootstrap_admin

if __name__ == "__main__":
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Bootstrapping admin...")
    _bootstrap_admin()
    print("Bootstrap complete!")
