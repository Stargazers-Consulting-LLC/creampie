import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

if __debug__:
    SQLALCHEMY_DATABASE_URL = "postgresql://creamapp:creamapp@localhost/cream"
else:
    SQLALCHEMY_DATABASE_URL = os.getenv("POSTGRESQL_URL", "")

if not SQLALCHEMY_DATABASE_URL:
    raise RuntimeError("Missing connection arguments: SQLALCHEMY_DATABASE_URL")

assert isinstance(SQLALCHEMY_DATABASE_URL, str)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

ModelBase = declarative_base()
