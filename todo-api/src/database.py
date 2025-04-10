import os
from fastapi import HTTPException
from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base 
from dotenv import load_dotenv

Base = declarative_base()

# Load environment variables from the .env file
load_dotenv()

# Retrieve the individual database connection components from environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

# Assemble the SQLAlchemy database URL
SQLALCHEMY_DATABASE_URL = f"mariadb+mariadbconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
print("SQL CON STRING")
print(SQLALCHEMY_DATABASE_URL)

# Create the engine for the database connection
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# Create a session local factory that binds to the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session
def get_db():
    try:
        db = SessionLocal()
        yield db
    except sqlalchemy.exc.SQLAlchemyError as e:
        # Log the error if needed
        print(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error: Could not connect to the database.")
    finally:
        try:
            db.close()
        except Exception as e:
            print(f"Error closing database session: {e}")
