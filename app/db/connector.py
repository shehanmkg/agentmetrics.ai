"""PostgreSQL database connector for the KPI Analytics System."""
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

from app.config import settings

logger = logging.getLogger(__name__)

class DatabaseConnector:
    """Database connector for PostgreSQL."""
    
    def __init__(self, database_url=None):
        """Initialize the database connector."""
        self.database_url = database_url or settings.DATABASE_URL
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    @contextmanager
    def get_session(self):
        """Get a database session with context management."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            session.close()
    
    def execute_query(self, query, params=None):
        """Execute a raw SQL query and return the results."""
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            return result.fetchall()
    
    def test_connection(self):
        """Test the database connection."""
        try:
            self.execute_query("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
    
    def get_table_column_info(self, table_name):
        """Get column information for a table."""
        query = """
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = :table_name
        """
        return self.execute_query(query, {"table_name": table_name})
    
    def count_records(self, table_name):
        """Count records in a table."""
        query = f"SELECT COUNT(*) FROM {table_name}"
        result = self.execute_query(query)
        return result[0][0] if result else 0


# Create a singleton instance
db_connector = DatabaseConnector() 