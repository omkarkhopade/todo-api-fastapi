from app.db.base_class import Base
from app.db.session import engine
from app.models.user import User
from app.models.task import Task


def init_db():
    pass # Alembic will handle database initialization and migrations
    """
    Initialize database tables.
    Creates all tables defined in models.
    """
    Base.metadata.create_all(bind=engine)
