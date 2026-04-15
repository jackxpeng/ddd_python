from typing import Optional
from datetime import date
from dataclasses import dataclass

@dataclass(frozen=True)
class OrderLine:
    order_id: str
    sku: str
    qty: int

class Batch:
    def __init__(self, ref_id: str, sku: str, qty: int, eta: Optional[date|None]):
        self.ref_id = ref_id
        self.sku = sku
        self.qty = qty
        self.eta = eta
        self.allocations: list[OrderLine] = []

    def allocate(self, order: OrderLine):
        raise NotImplementedError
    
    @property
    def available_quantity(self):
        return self.qty - sum(o.qty for o in self.allocations)

    