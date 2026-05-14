from abc import ABC, abstractmethod

from allocation.domain.model import Product

class AbstractRepository(ABC):
    def __init__(self):
        self.seen = set()   # track loaded products

    # template method pattern
    def add(self, product: Product):
        self._add(product)
        self.seen.add(product)
    
    def get(self, sku: str) -> Product | None:
        product = self._get(sku)
        if product:
            # ?? We even track reads ??
            # I guess ok because if it has no events, then there's nothing to handle
            # We track seen from repo methods so we don't have to check all products in the db
            self.seen.add(product)
        return product

    @abstractmethod
    def _add(self, product: Product):
        raise NotImplementedError

    @abstractmethod
    def _get(self, sku: str) -> Product | None:
        raise NotImplementedError

class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session
        super().__init__()
    
    def _add(self, product: Product):
        self.session.add(product)
    
    def _get(self, sku: str) -> Product | None:
        return self.session.query(Product).filter_by(sku=sku).first()
