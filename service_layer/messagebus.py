from typing import Dict, Type
from domain import events

def send_out_of_stock_notification(event: events.OutOfStock):

    print(f"SENDING EMAIL: Out of stock for {event.sku}")

HANDLERS: Dict[Type[events.Event], list] = {
    events.OutOfStock: [send_out_of_stock_notification],
}

def handle(event: events.Event):
    for handler in HANDLERS.get(type(event), []):
        handler(event)