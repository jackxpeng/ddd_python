import pytest
from adapters.uow import AbstractUnitOfWork
from domain.model import Product, Batch, OrderLine
from adapters.repository import AbstractRepository
from service_layer.services import InvalidSku, allocate, deallocate


class FakeSession:
    def __init__(self):
        self.committed = False
    
    def commit(self):
        self.committed = True

class FakeRepository(AbstractRepository):
    def __init__(self, products):
        super().__init__()
        self._products = set(products)
    
    def _add(self, product: Product):
        self._products.add(product)
    
    def _get(self, sku: str) -> Product | None:
        return next((b for b in self._products if b.sku == sku), None)

class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.products = FakeRepository([])
        self.committed = False
    
    def _commit(self):
        self.committed = True
    
    def rollback(self):
        pass

def test_returns_allocation():

    with FakeUnitOfWork() as uow:
        uow.products.add(Product("BED", [Batch("ref01", "BED", 100)]))
        uow.products.add(Product("DESK", [Batch("ref02", "DESK", 10)]))

        line = OrderLine("order01", "BED", 1)

        # ref = allocate(line.order_id, line.sku, line.qty, repo, session)
        ref = allocate(line.order_id, line.sku, line.qty, uow)

    assert ref == "ref01"
    
def test_error_for_invalid_sku():


    with FakeUnitOfWork() as uow:
        uow.products.add(Product("BED", [Batch("ref01", "BED", 100)]))
        uow.products.add(Product("BED", [Batch("ref02", "DESK", 10)]))

        line = OrderLine("order01", "Cabinet", 1)

        with pytest.raises(InvalidSku):
            allocate(line.order_id, line.sku, line.qty, uow)

def test_commits():
    line = OrderLine("order01", "DESK", 1)

    with FakeUnitOfWork() as uow:
        uow.products.add(Product("BED", [Batch("ref01", "BED", 100)]))
        uow.products.add(Product("DESK", [Batch("ref02", "DESK", 10)]))

        allocate(line.order_id, line.sku, line.qty, uow)

    assert uow.committed

def test_deallocate():
    '''
    Customers cancel orders. It happens all the time. Right now, if someone 
    cancels their order for a HIPSTER-WORKBENCH, that stock remains allocated to
    a dead order. We have absolutely no way to put it back into the available 
    inventory pool.
    I need a new feature: deallocate. When a cancellation comes in, I need the 
    system to find that batch, remove the customer's order line, and free up that 
    quantity for the next buyer.
    '''
    line = OrderLine("order01", "DESK", 1)

    with FakeUnitOfWork() as uow:
        uow.products.add(Product("BED", [Batch("ref01", "BED", 100)]))
        uow.products.add(Product("DESK", [Batch("ref02", "DESK", 10)]))
        ref_id = allocate(line.order_id, line.sku, line.qty, uow)

        product = uow.products.get("DESK")
        assert product is not None
        batch = next(b for b in product.batches if b.ref_id == "ref02")
        assert(batch is not None)
        assert(batch.available_quantity == 10-1)

        deallocate(line.order_id, line.sku, line.qty, uow)

        # No need to load batch again? deallocate manipulates batch in memory?
        # I guess that's the whole point of using ddd to abstract away infra like db
        assert(batch.available_quantity == 10)
    