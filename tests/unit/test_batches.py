from datetime import date
from domain.model import Batch, OrderLine

def test_allocate_reduces_available_quantity():
    """Verify that allocating reduces the batch's available_quantity by the correct amount."""
    batch = Batch("batch-001", "WIDGET", qty=100, eta=date(2024, 12, 25))
    line = OrderLine("order-001", "WIDGET", qty=40)
    
    batch.allocate(line)
    
    assert batch.available_quantity == 60

def test_allocate_fails_not_enough():
    batch = Batch("batch-002", "DESK", qty=100)
    line = OrderLine("order-002", "DESK", qty=101)
    
    assert batch.can_allocate(line) == False

def test_allocate_fails_wrong_sku():
    batch = Batch("batch-002", "DESK", qty=100)
    line = OrderLine("order-002", "CHAIR", qty=1)
    
    assert batch.can_allocate(line) == False
    
def test_allocate_ok_enough():
    batch = Batch("batch-002", "DESK", qty=100)
    line = OrderLine("order-002", "DESK", qty=100)
    
    assert batch.can_allocate(line) == True

def test_allocation_is_idempotent():
    batch = Batch("batch-002", "DESK", qty=100)
    line = OrderLine("order-002", "DESK", qty=1)
    
    assert batch.allocate(line) == True

    assert batch.allocate(line) == False
