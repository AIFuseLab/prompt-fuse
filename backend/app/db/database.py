from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

password = quote_plus("P@ss01409")
# SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:{password}@localhost:5432/prompt_manager"
SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:{password}@db:5432/prompt_manager"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print(f"Database error: {str(e)}")
    finally:
        db.close()