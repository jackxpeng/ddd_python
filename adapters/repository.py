from abc import ABC, abstractmethod

from domain.model import Product

class AbstractRepository(ABC):
    @abstractmethod
    def add(self, product: Product):
        raise NotImplementedError

    @abstractmethod
    def get(self, sku: str) -> Product | None:
        raise NotImplementedError

    @abstractmethod
    def list(self):
        raise NotImplementedError

class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session
    
    def add(self, product: Product):
        self.session.add(product)
    
    def get(self, sku: str) -> Product | None:
        return self.session.query(Product).filter_by(sku=sku).first()

    def list(self):
        return self.session.query(Product).all()
    
