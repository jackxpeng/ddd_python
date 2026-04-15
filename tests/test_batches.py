from datetime import date
from domain.model import Batch, OrderLine

def test_allocate_reduces_available_quantity():
    """Verify that allocating reduces the batch's available_quantity by the correct amount."""
    batch = Batch("batch-001", "WIDGET", qty=100, eta=date(2024, 12, 25))
    line = OrderLine("order-001", "WIDGET", qty=40)
    
    batch.allocate(line)
    
    assert batch.available_quantity == 60
