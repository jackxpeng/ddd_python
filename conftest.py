import os
import socket
import subprocess
import time

import pytest
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, clear_mappers, close_all_sessions

from adapters.orm import metadata_obj, start_mappers
import config


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
    """Automates a tunnel to K8s Postgres and manages the schema."""
    port = get_free_port()
    print(f"\n[Setup] Opening K8s Postgres tunnel on port {port}...")

    process = subprocess.Popen(
        ["kubectl", "port-forward", "service/postgres", f"{port}:5432"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Tell SQLAlchemy to use this random port instead of 5432
    os.environ["DB_PORT"] = str(port)
    os.environ["DB_HOST"] = "127.0.0.1"
    engine = create_engine(config.get_postgres_uri(), isolation_level="REPEATABLE READ")

    for _ in range(10):
        try:
            with engine.connect():
                break
        except Exception:
            time.sleep(0.5)
    else:
        process.terminate()
        pytest.fail("Failed to connect to Postgres via tunnel.")

    # NUKE AND PAVE (Using the real K8s database!)
    metadata_obj.drop_all(engine)
    metadata_obj.create_all(engine)

    yield engine

    # Tell SqlAlchemy to clearnly close the connection pool
    engine.dispose()

    print(f"\n[Teardown] Closing K8s Postgres tunnel on port {port}...")
    process.terminate()
    process.wait()

@pytest.fixture
def postgres_session_factory(postgres_db):
    start_mappers()
    # Notice we use the Postgres engine here
    factory = sessionmaker(bind=postgres_db)
    yield factory
    clear_mappers()

@pytest.fixture(autouse=True)
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
def add_stock(postgres_db):
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


def get_free_port():
    """Asks the OS for a random, guaranteed-free port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def api_url():
    """Automatically manages the K8s network tunnel for E2E tests."""
    port = get_free_port()

    print(f"\n[Setup] Opening K8s tunnel on port {port}...")

    # Spawn the tunnel as a background process
    process = subprocess.Popen(
        ["kubectl", "port-forward", "service/allocation-service", f"{port}:80"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    url = f"http://localhost:{port}"

    # Wait for the tunnel to actually open (ping it until it responds)
    for _ in range(10):
        try:
            requests.get(
                url
            )  # It might return 404, but we just care the connection works
            break
        except requests.ConnectionError:
            time.sleep(0.5)
    else:
        process.terminate()
        pytest.fail("Failed to open port-forward tunnel to Kubernetes.")

    # Give the URL to the test
    yield url

    # Teardown: Kill the background process when tests finish
    print(f"\n[Teardown] Closing K8s tunnel on port {port}...")
    process.terminate()
    process.wait()
