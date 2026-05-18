from dataclasses import dataclass
from datetime import date


class Event:
    pass


@dataclass
class OutOfStock(Event):
    sku: str


@dataclass
class Allocated(Event):
    order_id: str
    sku: str
    qty: int
    batchref: str

@dataclass
class Deallocated(Event):
    order_id: str
    sku: str
    qty: int

