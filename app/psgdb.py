import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Database connection string
DATABASE_URL = f"postgresql://user:password@pg-db:5432/taskdb"

# Create a new SQLAlchemy engine instance
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
session = sessionmaker(bind=engine)

# Base class for declarative models
Base = declarative_base()
