from domain import model
from adapters.repository import AbstractRepository
from adapters.uow import AbstractUnitOfWork

class InvalidSku(Exception):
    pass

# returns ref id of the batched allocated from
def allocate(order_id: str, sku: str, qty: int, uow: AbstractUnitOfWork) -> str:
    with uow:
        batches = [b for b in uow.batches.list() if b.sku == sku]
        if not batches:
            raise InvalidSku(f"Invalid sku: {sku}")
        line = model.OrderLine(order_id, sku, qty)
        ref_id = model.allocate(line, batches)
        uow.commit()
        return ref_id
           
def deallocate(order_id: str, sku: str, qty: int, uow: AbstractUnitOfWork) -> None:
    with uow:
        batches = [b for b in uow.batches.list() if b.sku == sku]
        if not batches:
            return
        line = model.OrderLine(order_id, sku, qty)
        model.deallocate(line, batches)
        uow.commit()