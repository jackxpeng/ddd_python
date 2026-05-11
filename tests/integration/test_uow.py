from adapters.uow import SqlAlchemyUnitOfWork
from domain import model
import pytest

def insert_batch(session, ref_id, sku, qty, eta):
    session.execute(
        'INSERT INTO batches (ref_id, sku, qty, eta)'
        ' VALUES (:ref_id, :sku, :qty, :eta)',
        dict(ref_id=ref_id, sku=sku, qty=qty, eta=eta)
    )

def get_allocated_batch_ref(session, order_id, sku):
    [[orderlineid]] = session.execute(
        'SELECT id FROM orderlines WHERE order_id=:order_id '
        'AND sku=:sku',
        dict(order_id=order_id, sku=sku)
    )
    [[batchref]] = session.execute(
        'SELECT b.ref_id FROM allocations JOIN batches AS '
        'b ON batch_id = b.id'
        ' WHERE orderline_id=:orderline_id',
        dict(orderline_id=orderlineid)
    )
    return batchref

def test_uow_can_retrieve_a_batch_and_allocate_to_it(session_factory):
    session = session_factory()
    insert_batch(session, 'batch1', 'HIPSTER-WORKBENCH', 100, None)
    session.commit()
    
    with SqlAlchemyUnitOfWork(session_factory) as uow:
        batch = uow.batches.get(ref_id='batch1')
        assert batch is not None
        line = model.OrderLine('o1', 'HIPSTER-WORKBENCH', 10)
        batch.allocate(line)
        uow.commit()
    
    batchref = get_allocated_batch_ref(session, 'o1', 'HIPSTER-WORKBENCH')
    assert batchref == 'batch1'
    
def test_rolls_back_uncommitted_work_by_default(session_factory):
    uow = SqlAlchemyUnitOfWork(session_factory)
    with uow:
        insert_batch(uow.session, "batch1", "PLINTH", 100, None)
    
    new_session = session_factory()
    rows = list(new_session.execute('SELECT * FROM "batches"'))
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
    rows = list(new_session.execute('SELECT * FROM "batches"'))
    assert rows == []