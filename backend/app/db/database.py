from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

password = quote_plus("P@ss01409")
# SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:{password}@localhost:5432/prompt_manager"
SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:{password}@db:5432/prompt_fuse"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# inspector = inspect(engine)
# columns = inspector.get_columns('llm')
# # Print the column details
# for column in columns:
#     print(f"Column: {column['name']}, Type: {column['type']}, Nullable: {column['nullable']}, Default: {column['default']}")

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print(f"Database error: {str(e)}")
        raise
    finally:
        db.close()