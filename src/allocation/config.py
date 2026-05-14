import os

def get_postgres_uri():
    host = os.environ.get("DB_HOST", "127.0.0.1")
    port = os.environ.get("DB_PORT", 54322)
    password = os.environ.get("DB_PASSWORD", "abc123")
    user, db_name = "allocation", "allocation"
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

def get_api_url():
    host = os.environ.get("API_HOST", "localhost")
    port = os.environ.get("API_PORT", 5005)
    return f"http://{host}:{port}"