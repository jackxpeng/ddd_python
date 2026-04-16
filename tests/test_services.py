import pytest
from domain.model import Batch, OrderLine
from adapters.repository import FakeRepository
from services.services import InvalidSku, allocate

class FakeSession:
    def __init__(self):
        self.committed = False
    
    def commit(self):
        self.committed = True

def test_returns_allocation():
    repo = FakeRepository()

    session = FakeSession()

    repo.add(Batch("ref01", "BED", 100))
    repo.add(Batch("ref02", "DESK", 10))

    line = OrderLine("order01", "BED", 1)

    ref = allocate(line.order_id, line.sku, line.qty, repo, session)

    assert ref == "ref01"
    
def test_error_for_invalid_sku():
    repo = FakeRepository()

    session = FakeSession()

    repo.add(Batch("ref01", "BED", 100))
    repo.add(Batch("ref02", "DESK", 10))

    line = OrderLine("order01", "Cabinet", 1)

    with pytest.raises(InvalidSku):
        allocate(line.order_id, line.sku, line.qty, repo, session)

def test_commits():
    line = OrderLine("order01", "DESK", 1)
    repo = FakeRepository()
    repo.add(Batch("ref01", "BED", 100))
    repo.add(Batch("ref02", "DESK", 10))

    session = FakeSession()

    allocate(line.order_id, line.sku, line.qty, repo, session)

    assert session.committed
