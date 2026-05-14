from datetime import date
from allocation.domain import model
from allocation.adapters.repository import AbstractRepository
from allocation.service_layer import unit_of_work


class InvalidSku(Exception):
    pass


def add_batch(
    ref: str, sku: str, qty: int, eta: date | None, uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        product = uow.products.get(sku=sku)
        if product is None:
            product = model.Product(sku, batches=[])
            uow.products.add(product)
        product.batches.append(model.Batch(ref, sku, qty, eta))
        uow.commit()


# returns ref id of the batched allocated from
def allocate(
    order_id: str, sku: str, qty: int, uow: unit_of_work.AbstractUnitOfWork
) -> str | None:
    with uow:
        product = uow.products.get(sku)
        if product is None:
            raise InvalidSku(f"Invalid sku: {sku}")
        line = model.OrderLine(order_id, sku, qty)
        ref_id = product.allocate(line)
        uow.commit()

    return ref_id


def deallocate(order_id: str, sku: str, qty: int, uow: unit_of_work.AbstractUnitOfWork) -> None:
    with uow:
        product = uow.products.get(sku)
        if not product:
            return

        line = model.OrderLine(order_id, sku, qty)
        product.deallocate(line)

        uow.commit()
