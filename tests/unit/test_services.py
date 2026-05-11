import pytest
from adapters.uow import AbstractUnitOfWork
from domain.model import Batch, OrderLine
from adapters.repository import AbstractRepository
from service_layer.services import InvalidSku, allocate


class FakeSession:
    def __init__(self):
        self.committed = False
    
    def commit(self):
        self.committed = True

class FakeRepository(AbstractRepository):
    def __init__(self):
        self.batches = []
    
    def add(self, batch: Batch):
        self.batches.append(batch)
    
    def get(self, ref_id: str) -> Batch | None:
        return next((b for b in self.batches if b.ref_id == ref_id), None)

    def list(self):
        return self.batches

class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.batches = FakeRepository()
        self.committed = False
    
    def commit(self):
        self.committed = True
    
    def rollback(self):
        pass

def test_returns_allocation():

    with FakeUnitOfWork() as uow:
        uow.batches.add(Batch("ref01", "BED", 100))
        uow.batches.add(Batch("ref02", "DESK", 10))

        line = OrderLine("order01", "BED", 1)

        # ref = allocate(line.order_id, line.sku, line.qty, repo, session)
        ref = allocate(line.order_id, line.sku, line.qty, uow)

    assert ref == "ref01"
    
def test_error_for_invalid_sku():


    with FakeUnitOfWork() as uow:
        uow.batches.add(Batch("ref01", "BED", 100))
        uow.batches.add(Batch("ref02", "DESK", 10))

        line = OrderLine("order01", "Cabinet", 1)

        with pytest.raises(InvalidSku):
            allocate(line.order_id, line.sku, line.qty, uow)

def test_commits():
    line = OrderLine("order01", "DESK", 1)

    with FakeUnitOfWork() as uow:
        uow.batches.add(Batch("ref01", "BED", 100))
        uow.batches.add(Batch("ref02", "DESK", 10))

        allocate(line.order_id, line.sku, line.qty, uow)

    assert uow.committed
