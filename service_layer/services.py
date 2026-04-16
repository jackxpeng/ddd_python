from domain import model
from adapters.repository import AbstractRepository

class InvalidSku(Exception):
    pass

# returns ref id of the batched allocated from
def allocate(order_id: str, sku: str, qty: int, repo: AbstractRepository, session) -> str:
    batches = [b for b in repo.list() if b.sku == sku]
    if not batches:
        raise InvalidSku(f"Invalid sku: {sku}")
    line = model.OrderLine(order_id, sku, qty)
    ref_id = model.allocate(line, batches)
    session.commit()
    return ref_id
           
    