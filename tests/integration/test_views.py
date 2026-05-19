# pylint: disable=redefined-outer-name
from datetime import date
from unittest import mock
import pytest
from allocation import bootstrap, views
from allocation.domain import commands
from allocation.service_layer import unit_of_work

today = date.today()

@pytest.fixture
def sqlite_bus(session_factory):
    bus = bootstrap.bootstrap(
        start_orm=False,
        uow=unit_of_work.SqlAlchemyUnitOfWork(session_factory),
        notifications=mock.Mock(),
        publish=lambda *args: None,
    )
    yield bus

def test_allocations_view(sqlite_bus, session_factory):
    sqlite_bus.handle(commands.CreateBatch("sku1batch", "sku1", 50, None))
    sqlite_bus.handle(commands.CreateBatch("sku2batch", "sku2", 50, today))
    sqlite_bus.handle(commands.Allocate("order1", "sku1", 20))
    sqlite_bus.handle(commands.Allocate("order1", "sku2", 20))
    # add a spurious batch and order to make sure we're getting the right ones
    sqlite_bus.handle(commands.CreateBatch("sku1batch-later", "sku1", 50, today))
    sqlite_bus.handle(commands.Allocate("otherorder", "sku1", 30))
    sqlite_bus.handle(commands.Allocate("otherorder", "sku2", 10))

    session = session_factory()
    try:
        assert views.allocations("order1", session) == [
            {"sku": "sku1", "batchref": "sku1batch"},
            {"sku": "sku2", "batchref": "sku2batch"},
        ]
    finally:
        session.close()

def test_deallocation(sqlite_bus, session_factory):
    sqlite_bus.handle(commands.CreateBatch("b1", "sku1", 50, None))
    sqlite_bus.handle(commands.CreateBatch("b2", "sku1", 50, today))
    sqlite_bus.handle(commands.Allocate("o1", "sku1", 40))
    sqlite_bus.handle(commands.ChangeBatchQuantity("b1", 10))

    session = session_factory()
    try:
        assert views.allocations("o1", session) == [
            {"sku": "sku1", "batchref": "b2"},
        ]
    finally:
        session.close()
