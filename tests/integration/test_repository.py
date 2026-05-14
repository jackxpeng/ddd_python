from allocation.domain.model import Batch, Product
from allocation.adapters.repository import SqlAlchemyRepository

from sqlalchemy import text
def test_repository_can_save_a_batch(session):
    batch = Batch("batch01", "DESK", 100)
    product = Product("DESK", [batch])
    repo = SqlAlchemyRepository(session)
    repo.add(product)
    session.commit()
    
    rows = list(session.execute(text('SELECT ref_id, sku, qty, eta FROM batches')))
    assert rows == [("batch01", "DESK", 100, None)]