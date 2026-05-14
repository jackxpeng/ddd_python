from domain import model
from adapters.repository import AbstractRepository
from service_layer.uow import AbstractUnitOfWork

class InvalidSku(Exception):
    pass

# returns ref id of the batched allocated from
def allocate(order_id: str, sku: str, qty: int, uow: AbstractUnitOfWork) -> str:
    with uow:
        product = uow.products.get(sku)
        if product is None:
            raise InvalidSku(f"Invalid sku: {sku}")
        line = model.OrderLine(order_id, sku, qty)
        ref_id = product.allocate(line)
        uow.commit()

    return ref_id
           
def deallocate(order_id: str, sku: str, qty: int, uow: AbstractUnitOfWork) -> None:
    with uow:
        product = uow.products.get(sku)
        if not product:
            return
        
        line = model.OrderLine(order_id, sku, qty)
        product.deallocate(line)
        
        uow.commit()