import time
import pytest
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, clear_mappers, close_all_sessions

from allocation.adapters.orm import metadata_obj, start_mappers
import allocation.config as config


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    metadata_obj.create_all(engine)
    yield engine
    metadata_obj.drop_all(engine)


@pytest.fixture
def session(in_memory_db):
    start_mappers()
    session = sessionmaker(bind=in_memory_db)()
    yield session
    session.close()
    clear_mappers()


@pytest.fixture
def session_factory(in_memory_db):
    start_mappers()
    session_factory = sessionmaker(bind=in_memory_db)
    yield session_factory
    close_all_sessions()
    clear_mappers()


@pytest.fixture(scope="session")
def postgres_db():
    engine = create_engine(config.get_postgres_uri(), isolation_level="REPEATABLE READ")

    for _ in range(10):
        try:
            with engine.connect():
                break
        except Exception:
            time.sleep(0.5)
    else:
        pytest.fail("Failed to connect to Postgres.")

    metadata_obj.drop_all(engine)
    metadata_obj.create_all(engine)

    yield engine

    engine.dispose()

@pytest.fixture
def postgres_session_factory(postgres_db):
    start_mappers()
    # Notice we use the Postgres engine here
    factory = sessionmaker(bind=postgres_db)
    yield factory
    clear_mappers()

@pytest.fixture
def clear_db_between_tests(postgres_db):
    """
    Automatically runs before EVERY test to ensure a clean slate.
    Using DELETE instead of TRUNCATE is often faster for small test datasets.
    """
    with postgres_db.begin() as conn:
        # Delete data from all tables (order matters if you have foreign keys!)
        conn.execute(text("DELETE FROM allocations"))
        conn.execute(text("DELETE FROM orderlines"))
        conn.execute(text("DELETE FROM batches"))
        conn.execute(text("DELETE FROM products"))
    
    yield # The test runs here, with a perfectly clean database

# 2. the reusable data setup/teardown fixture
@pytest.fixture
def add_stock(postgres_db, clear_db_between_tests):
    def _add_stock(lines):
        added_skus = set()
        with postgres_db.begin() as conn:
            for ref, sku, qty, eta in lines:
                if sku not in added_skus:
                    conn.execute(
                        text(
                            "INSERT INTO products (sku, version_number) VALUES (:sku, :version_number)"
                        ),
                        {"sku": sku, "version_number": 0},
                    )
                    added_skus.add(sku)
                conn.execute(
                    text(
                        "INSERT INTO batches (ref_id, sku, qty, eta) VALUES (:ref, :sku, :qty, :eta)"
                    ),
                    {"ref": ref, "sku": sku, "qty": qty, "eta": eta},
                )

    yield _add_stock





@pytest.fixture(scope="session")
def api_url():
    url = config.get_api_url()

    for _ in range(10):
        try:
            requests.get(url)
            break
        except requests.ConnectionError:
            time.sleep(0.5)
    else:
        pytest.fail("Failed to connect to API.")

    yield url
