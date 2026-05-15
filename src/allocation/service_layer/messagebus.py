from typing import List, Dict, Callable, Type
from allocation.domain import events
from allocation.service_layer import unit_of_work, handlers


def handle(event: events.Event, uow: unit_of_work.AbstractUnitOfWork):
    results = []
    queue = [event]
    while queue:
        event = queue.pop(0)
        for handler in HANDLERS.get(type(event), []):
            results.append(handler(event, uow=uow))
            queue.extend(uow.collect_new_events())
    return results



HANDLERS: Dict[Type[events.Event], List[Callable]] = {
    events.BatchCreated: [handlers.add_batch],
    events.AllocationRequired: [handlers.allocate],
    events.BatchQuantityChanged: [handlers.batch_quantity_change],
    events.OutOfStock: [handlers.send_out_of_stock_notification],
}
