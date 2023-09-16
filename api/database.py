from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set up the database connection
DATABASE_URL = "mysql+mysqlconnector://aws:aws@10.22.0.140/aws_database"
engine = create_engine(DATABASE_URL)

# Create a session to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
