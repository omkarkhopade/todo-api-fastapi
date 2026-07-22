from app.db.base_class import Base
from app.db.session import engine
from app.models import task, user  # noqa: F401 -- register model tables


def init_db():
    """
    Initialize tables for disposable development environments.

    Production deployments must use Alembic migrations instead.
    """
    Base.metadata.create_all(bind=engine)
