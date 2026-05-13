import pytest
from datetime import date
from domain.model import Product, OrderLine, Batch, OutOfStock


def test_prefers_warehouse_batches_to_shipments():
    batch1 = Batch("batch-1", "CHAIR", 100, date(2026, 4, 17))
    batch2 = Batch("batch-2", "CHAIR", 30)
    batches = [batch1, batch2]
    product = Product(sku="CHAIR", batches=batches)

    line = OrderLine("order-1", "CHAIR", 10)

    assert product.allocate(line) == batch2.ref_id
    assert batch1.available_quantity == batch1.qty
    assert batch2.available_quantity == batch2.qty - line.qty


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch1 = Batch("batch-1", "CHAIR", 100, date(2026, 4, 17))
    batch2 = Batch("batch-2", "CHAIR", 30)
    batches = [batch1, batch2]

    product = Product(sku="CHAIR", batches=batches)

    line = OrderLine("order-1", "CHAIR", 101)
    with pytest.raises(OutOfStock):
        product.allocate(line)

def test_increments_version_number():
    line = OrderLine("order-1", "CHAIR", 10)
    product = Product(
        sku="CHAIR", batches=[Batch("batch-1", "CHAIR", 100)]
    )
    product.version_number = 7
    product.allocate(line)
    assert product.version_number == 8    