import threading
import time
from adapters.uow import SqlAlchemyUnitOfWork
from domain import model
import pytest
from sqlalchemy.orm.exc import StaleDataError
from sqlalchemy import text

def insert_batch(session, ref_id, sku, qty, eta):
    session.execute(
        text("INSERT INTO products (sku, version_number) VALUES (:sku, :version_number)"),
        dict(sku=sku, version_number=0),
    )
    session.execute(
        text("INSERT INTO batches (ref_id, sku, qty, eta) VALUES (:ref_id, :sku, :qty, :eta)"),
        dict(ref_id=ref_id, sku=sku, qty=qty, eta=eta),
    )


def get_allocated_batch_ref(session, order_id, sku):
    [[orderlineid]] = session.execute(
        text("SELECT id FROM orderlines WHERE order_id=:order_id AND sku=:sku"),
        dict(order_id=order_id, sku=sku),
    )
    [[batchref]] = session.execute(
        text("SELECT b.ref_id FROM allocations JOIN batches AS b ON batch_id = b.id WHERE orderline_id=:orderline_id"),
        dict(orderline_id=orderlineid),
    )
    return batchref


def test_uow_can_retrieve_a_product_and_allocate_to_it(session_factory):
    session = session_factory()
    insert_batch(session, "batch1", "HIPSTER-WORKBENCH", 100, None)
    session.commit()

    with SqlAlchemyUnitOfWork(session_factory) as uow:
        product = uow.products.get(sku="HIPSTER-WORKBENCH")
        assert product is not None
        line = model.OrderLine("o1", "HIPSTER-WORKBENCH", 10)
        product.allocate(line)
        uow.commit()

    batchref = get_allocated_batch_ref(session, "o1", "HIPSTER-WORKBENCH")
    assert batchref == "batch1"


def test_rolls_back_uncommitted_work_by_default(session_factory):
    uow = SqlAlchemyUnitOfWork(session_factory)
    with uow:
        insert_batch(uow.session, "batch1", "PLINTH", 100, None)

    new_session = session_factory()
    rows = list(new_session.execute(text('SELECT * FROM "batches"')))
    assert rows == []


def test_rolls_back_on_error(session_factory):
    class MyException(Exception):
        pass

    uow = SqlAlchemyUnitOfWork(session_factory)
    with pytest.raises(MyException):
        with uow:
            insert_batch(uow.session, "batch1", "LARGE-FORK", 100, None)
            raise MyException()

    new_session = session_factory()
    rows = list(new_session.execute(text('SELECT * FROM "batches"')))
    assert rows == []


def try_to_allocate(order_id, sku, exceptions, session_factory):
    try:
        with SqlAlchemyUnitOfWork(session_factory) as uow:
            product = uow.products.get(sku=sku)
            assert product is not None
            line = model.OrderLine(order_id, sku, 10)
            product.allocate(line)

            # Artificial delay to guarantee a race condition
            time.sleep(0.2)

            uow.commit()
    except Exception as e:
        exceptions.append(e)


def test_concurrent_updates_to_version_are_not_allowed(postgres_session_factory, clear_db_between_tests):
    sku, batch_ref = "CONCURRENT-DESK", "batch1"
    session = postgres_session_factory()
    insert_batch(session, batch_ref, sku, 100, None)
    session.commit()

    exceptions = []

    # Spawn two threads trying to allocate at the exact same time
    thread1 = threading.Thread(
        target=try_to_allocate, args=("order1", sku, exceptions, postgres_session_factory)
    )
    thread2 = threading.Thread(
        target=try_to_allocate, args=("order2", sku, exceptions, postgres_session_factory)
    )

    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    [[version]] = session.execute(
        text("SELECT version_number FROM products WHERE sku=:sku"),
        dict(sku=sku),
    )

    # We expect one thread to succeed (bumping version to 1)
    # and the other to fail with a concurrency exception.
    assert version == 1
    assert len(exceptions) == 1
    # Best practice for DB-level isolation locks: assert the string contains the native DB error
    assert "could not serialize access due to concurrent update" in str(exceptions[0])    

    session.close()
