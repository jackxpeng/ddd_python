from sqlalchemy import create_engine
from adapters.orm import metadata_obj, start_mappers
import config # Add this

if __name__ == "__main__":
    print("Initializing Database Schema...")
    # Change this line:
    engine = create_engine(config.get_postgres_uri()) 
    metadata_obj.create_all(engine)
    print("Schema initialization complete!")