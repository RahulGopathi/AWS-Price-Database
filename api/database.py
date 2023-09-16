from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decouple import config

# Set up the database connection
DATABASE_URL = f"mysql+mysqlconnector://{config('DB_USER')}:{config('DB_PASSWORD')}@{config('DB_HOST')}/{config('DB_NAME')}"
engine = create_engine(DATABASE_URL)

# Create a session to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
