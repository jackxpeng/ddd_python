from dataclasses import asdict

from allocation.domain import model, events, commands
from allocation.service_layer import unit_of_work
from allocation.adapters import email, redis_eventpublisher


class InvalidSku(Exception):
    pass


class InvalidBatchReference(Exception):
    pass


def add_batch(event: commands.CreateBatch, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        product = uow.products.get(sku=event.sku)
        if product is None:
            product = model.Product(event.sku, batches=[])
            uow.products.add(product)
        product.batches.append(model.Batch(event.ref, event.sku, event.qty, event.eta))
        uow.commit()


def allocate(event: commands.Allocate, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        product = uow.products.get(event.sku)
        if product is None:
            raise InvalidSku(f"Invalid sku: {event.sku}")
        line = model.OrderLine(event.order_id, event.sku, event.qty)
        product.allocate(line)
        uow.commit()


def reallocate(
    event: events.Deallocated,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        product = uow.products.get(sku=event.sku)
        if product is None:
            raise InvalidSku(f"Invalid sku: {event.sku}")
        # We translate the event directly into a command
        product.events.append(commands.Allocate(**asdict(event)))
        uow.commit()


def batch_quantity_change(
    event: commands.ChangeBatchQuantity, uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        # load product (root) using batch id in event
        product = uow.products.get_by_batchref(event.ref)
        if product is None:
            raise InvalidBatchReference(f"Unable to find batch reference {event.ref}")
        product.change_batch_quantity(event.ref, event.qty)
        uow.commit()


def send_out_of_stock_notification(
    event: events.OutOfStock, uow: unit_of_work.AbstractUnitOfWork
):
    email.send("stock@made.com", f"Out of stock for {event.sku}")


def publish_allocated_event(
    event: events.Allocated, uow: unit_of_work.AbstractUnitOfWork
):
    redis_eventpublisher.publish("line_allocated", event)


def add_allocation_to_read_model(
    event: events.Allocated,
    uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        uow.session.execute(
            """
            INSERT INTO allocations_view (orderid, sku, batchref)
            VALUES (:orderid, :sku, :batchref)
            """,
            dict(orderid=event.order_id, sku=event.sku, batchref=event.batchref),
        )
        uow.commit()


def remove_allocation_from_read_model(
    event: events.Deallocated,
    uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        uow.session.execute(
            """
            DELETE FROM allocations_view
            WHERE orderid = :orderid AND sku = :sku
            """,
            dict(orderid=event.order_id, sku=event.sku),
        )
        uow.commit()
