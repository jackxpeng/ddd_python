from typing import List, Dict, Callable, Type
from allocation.domain import events
from allocation.adapters import email 

def handle(event: events.Event):
    for handler in HANDLERS.get(type(event), []):
        handler(event)

def send_out_of_stock_notification(event: events.OutOfStock):
    email.send_mail(
        "stock@made.com",
        f"Out of stock for {event.sku}"
    )

HANDLERS: Dict[Type[events.Event], List[Callable]] = {
    events.OutOfStock: [send_out_of_stock_notification],
} 
