import os
from fastapi import HTTPException
from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base 
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

# Load environment variables from the .env file
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
APP_DB_NAME = os.getenv("APP_DB_NAME")
DB_NAME = os.getenv("DB_NAME")
APP_DB_PORT = os.getenv("APP_DB_PORT")

missing_vars = []
if not DB_USER:
    missing_vars.append("DB_USER")
if not DB_PASSWORD:
    missing_vars.append("DB_PASSWORD")
if not APP_DB_NAME:
    missing_vars.append("APP_DB_NAME")
if not DB_NAME:
    missing_vars.append("DB_NAME")
if not APP_DB_PORT:
    missing_vars.append("APP_DB_PORT")

if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Assemble the SQLAlchemy database URL
SQLALCHEMY_DATABASE_URL = f"mariadb+mariadbconnector://{DB_USER}:{DB_PASSWORD}@{APP_DB_NAME}:{APP_DB_PORT}/{DB_NAME}"
logger.info(f"CON_STRING: mariadb://{DB_USER}:***@{APP_DB_NAME}:{APP_DB_PORT}/{DB_NAME}")

# Create the engine for the database connection
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# Create a session local factory that binds to the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    except sqlalchemy.exc.SQLAlchemyError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error: Could not connect to the database.")
    finally:
        try:
            db.close()
        except Exception as e:
            logger.error(f"Error closing database session: {e}")
