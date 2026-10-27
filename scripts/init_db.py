"""
SIH26263 APAAR Platform - Database Initialization and Seed Utility
Used in deployment pre-flight to guarantee database schema and synthetic demo accounts
are ready on first boot without manual SQL execution.
"""
import sys
import logging
from sqlalchemy import inspect

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("init_db")

def initialize_database():
    try:
        from backend.app.database import Base, engine, SessionLocal
        from backend.app.models.user import User
        from backend.app.seed.seed_data import seed_database
    except ImportError as e:
        logger.error(f"Failed to import application modules: {e}")
        sys.exit(1)

    url_str = engine.url.render_as_string(hide_password=True)
    logger.info(f"Target database: {url_str}")

    logger.info("Verifying / creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified.")

    db = SessionLocal()
    try:
        inspector = inspect(engine)
        if "users" in inspector.get_table_names():
            user_count = db.query(User).count()
            if user_count == 0:
                logger.info("Database has no users. Seeding synthetic demo data...")
                seed_database()
                logger.info("Synthetic demo data successfully seeded.")
            else:
                logger.info(f"Existing database active: {user_count} user(s) found. Preserving persistent data.")
        else:
            logger.info("Initializing schema and seeding demo data...")
            seed_database()
            logger.info("Synthetic demo data initialized.")
    except Exception as exc:
        logger.error(f"Error during database initialization: {exc}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    initialize_database()
