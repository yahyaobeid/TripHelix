# Import SQLAlchemy components for database management
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Import application settings
from app.core.config import settings

# Create SQLAlchemy engine with PostgreSQL connection
# The engine manages the connection pool and database connections
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)

# Create a session factory
# This will be used to create individual database sessions
SessionLocal = sessionmaker(
    autocommit=False,  # Don't automatically commit changes
    autoflush=False,  # Don't automatically flush changes
    bind=engine  # Bind to our engine
)

# Create a base class for declarative models
# All database models will inherit from this class
Base = declarative_base()

# Database dependency for FastAPI
def get_db():
    """
    Generator function that yields database sessions.
    This is used as a FastAPI dependency to provide database access to routes.
    
    Usage:
    @app.get("/items")
    def get_items(db: Session = Depends(get_db)):
        return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db  # Provide the database session to the route
    finally:
        db.close()  # Ensure the session is closed after use
