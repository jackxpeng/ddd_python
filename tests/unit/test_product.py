import pytest
from datetime import date
from allocation.domain.model import Product, OrderLine, Batch, OutOfStock
from allocation.domain import events


def test_prefers_warehouse_batches_to_shipments():
    batch1 = Batch("batch-1", "CHAIR", 100, date(2026, 4, 17))
    batch2 = Batch("batch-2", "CHAIR", 30)
    batches = [batch1, batch2]
    product = Product(sku="CHAIR", batches=batches)

    line = OrderLine("order-1", "CHAIR", 10)

    assert product.allocate(line) == batch2.ref_id
    assert batch1.available_quantity == batch1.qty
    assert batch2.available_quantity == batch2.qty - line.qty


def test_records_out_of_stock_event_if_cannot_allocate():
    batch = Batch("batch1", "SMALL-FORK", 10, eta=date.today())
    product = Product(sku="SMALL-FORK", batches=[batch])
    
    # We try to allocate a different SKU to force a failure
    different_sku_line = OrderLine("order2", "HEAVY-SPOON", 10)
    
    allocation = product.allocate(different_sku_line)
    
    # Notice we no longer assert a pytest.raises(OutOfStock)!
    # Instead, we check the product's internal events list.
    assert product.events[-1] == events.OutOfStock(sku="HEAVY-SPOON")
    assert allocation is None

def test_increments_version_number():
    line = OrderLine("order-1", "CHAIR", 10)
    product = Product(
        sku="CHAIR", batches=[Batch("batch-1", "CHAIR", 100)]
    )
    product.version_number = 7
    product.allocate(line)
    assert product.version_number == 8    