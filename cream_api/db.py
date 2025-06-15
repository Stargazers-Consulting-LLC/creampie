from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from cream_api.settings import Settings, get_app_config

# Get database configuration from settings
settings: Settings = get_app_config()
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://{settings.db_user}:{settings.db_password}@{settings.db_host}/{settings.db_name}"

if not SQLALCHEMY_DATABASE_URL:
    raise RuntimeError("Missing connection arguments: SQLALCHEMY_DATABASE_URL")

assert isinstance(SQLALCHEMY_DATABASE_URL, str)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

ModelBase = declarative_base()
