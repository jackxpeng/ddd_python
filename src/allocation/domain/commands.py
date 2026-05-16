from datetime import date
from dataclasses import dataclass

class Command:
    pass

@dataclass
class CreateBatch(Command):
    ref: str
    sku: str
    qty: int
    eta: date|None = None
@dataclass
class ChangeBatchQuantity(Command):
    ref: str
    qty: int

@dataclass
class Allocate(Command):
    order_id: str
    sku: str
    qty: int