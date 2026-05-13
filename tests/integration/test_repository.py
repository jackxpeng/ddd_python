from domain.model import Batch
from adapters.repository import SqlAlchemyRepository

from sqlalchemy import text
def test_repository_can_save_a_batch(session):
    batch = Batch("batch01", "DESK", 100)
    repo = SqlAlchemyRepository(session)
    repo.add(batch)
    session.commit()
    
    rows = list(session.execute(text('SELECT ref_id, sku, qty, eta FROM batches')))
    assert rows == [("batch01", "DESK", 100, None)]