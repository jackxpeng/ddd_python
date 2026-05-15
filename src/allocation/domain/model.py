from datetime import date
from dataclasses import dataclass
from allocation.domain import events


class OutOfStock(Exception):
    pass


@dataclass(unsafe_hash=True)
class OrderLine:
    order_id: str
    sku: str
    qty: int


class Batch:
    def __init__(self, ref_id: str, sku: str, qty: int, eta: date | None = None):
        self.ref_id = ref_id
        self.sku = sku
        self.qty = qty
        self.eta = eta
        self.allocations: set[OrderLine] = set()

    @property
    def available_quantity(self):
        return self.qty - sum(o.qty for o in self.allocations)

    def allocate(self, order: OrderLine) -> bool:
        if order in self.allocations:
            return False
        if not self.can_allocate(order):
            return False
        self.allocations.add(order)
        return True

    def can_allocate(self, order: OrderLine) -> bool:
        if self.sku != order.sku:
            return False
        return self.available_quantity >= order.qty

    def deallocate_one(self) -> OrderLine:
        # ?? handle the case of popping from empty set ??
        return self.allocations.pop()

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta


class Product:
    def __init__(self, sku: str, batches: list[Batch], version_number: int = 0):
        self.sku = sku
        # batches must be a reference so orm/sqlalchemy can track and persist
        self.batches = batches
        self.events = []
        self.version_number = version_number

    def allocate(self, order: OrderLine) -> str | None:
        self.batches.sort()
        for b in self.batches:
            if b.can_allocate(order):
                b.allocate(order)
                self.version_number += 1
                return b.ref_id
        # raise OutOfStock(f"Out of stock for sku {order.sku} and quantity {order.qty}")
        self.events.append(events.OutOfStock(order.sku))

    def deallocate(self, order: OrderLine) -> None:
        for b in self.batches:
            if order in b.allocations:
                b.allocations.discard(order)
                break

    def change_batch_quantity(self, batch_ref_id: str, qty: int):
        # when a precondition is violated, the domain should scream in its own language
        # raise BatchNotFound(f"No batch with ref {ref_id} in product {self.sku}")
        batch = next(b for b in self.batches if b.ref_id == batch_ref_id)
        batch.qty = qty

        while batch.available_quantity < 0:
            line = batch.deallocate_one()
            self.events.append(
                events.AllocationRequired(line.order_id, line.sku, line.qty)
            )
