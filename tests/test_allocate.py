from datetime import date
from domain.model import OrderLine, Batch, allocate


def test_prefers_warehouse_batches_to_shipments():
    line = OrderLine("order-1", "CHAIR", 10)
    batch1 = Batch("batch-1", "CHAIR", 100, date(2026, 4, 17))
    batch2 = Batch("batch-2", "CHAIR", 30)
    batches = [batch1, batch2]

    assert allocate(line, batches) == batch2.ref_id
    assert batch1.available_quantity == batch1.qty
    assert batch2.available_quantity == batch2.qty - line.qty

