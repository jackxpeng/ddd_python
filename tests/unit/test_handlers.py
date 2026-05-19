import pytest
from unittest import mock
from allocation.service_layer.unit_of_work import AbstractUnitOfWork
from allocation.service_layer import handlers
from allocation.domain.model import Product, Batch
from allocation.adapters.repository import AbstractRepository
from allocation.adapters import notifications
from allocation.service_layer.handlers import InvalidSku, allocate
from allocation.domain import events, commands
from allocation.service_layer import messagebus
from allocation import bootstrap


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

    def _get_by_batchref(self, batchref: str) -> Product | None:
        for product in self._products:
            for batch in product.batches:
                if batch.ref_id == batchref:
                    return product
        return None


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.products = FakeRepository([])
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass


def test_returns_allocation():

    uow = FakeUnitOfWork()
    uow.products.add(Product("BED", [Batch("ref01", "BED", 100)]))
    uow.products.add(Product("DESK", [Batch("ref02", "DESK", 10)]))

    command = commands.Allocate("order01", "BED", 1)

    handlers.allocate(command, uow)


def test_error_for_invalid_sku():

    uow = FakeUnitOfWork()

    uow.products.add(Product("BED", [Batch("ref01", "BED", 100)]))
    uow.products.add(Product("BED", [Batch("ref02", "DESK", 10)]))

    command = commands.Allocate("order01", "CABINET", 1)

    with pytest.raises(InvalidSku):
        allocate(command, uow)


def test_commits():

    uow = FakeUnitOfWork()
    uow.products.add(Product("BED", [Batch("ref01", "BED", 100)]))
    uow.products.add(Product("DESK", [Batch("ref02", "DESK", 10)]))

    command = commands.Allocate("order01", "DESK", 1)
    allocate(command, uow)

    assert uow.committed


def test_sends_email_on_out_of_stock_error():
    uow = FakeUnitOfWork()
    handlers.add_batch(commands.CreateBatch("b1", "POPULAR-CURTAINS", 9), uow)

    class FakeNotifications(notifications.AbstractNotifications):
        def __init__(self):
            self.sent = []
        def send(self, destination, message):
            self.sent.append((destination, message))
            
    fake_notifications = FakeNotifications()
    bus = bootstrap.bootstrap(
        start_orm=False, 
        uow=uow, 
        notifications=fake_notifications,
        publish=lambda *args: None,
    )

    command = commands.Allocate("o1", "POPULAR-CURTAINS", 10)
    bus.handle(command)

    assert fake_notifications.sent == [("stock@made.com", "Out of stock for POPULAR-CURTAINS")]
