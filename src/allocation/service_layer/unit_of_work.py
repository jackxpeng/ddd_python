from abc import ABC, abstractmethod
from allocation.adapters import repository
from allocation.adapters.repository import SqlAlchemyRepository
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import allocation.config as config

get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))

class AbstractUnitOfWork(ABC):
    products: repository.AbstractRepository
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc, tb):
        self.rollback()

    # template method pattern
    def commit(self):
        self._commit()
        
    def collect_new_events(self):
        for product in self.products.seen:
            while product.events:
                yield product.events.pop(0)
    
    @abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError

class SqlAlchemyUnitOfWork(AbstractUnitOfWork):

    def __init__(self, session_factory):
        self.session_factory = session_factory
    
    def __enter__(self):
        self.session = self.session_factory()
        self.products = SqlAlchemyRepository(self.session)
        return super().__enter__()

    def __exit__(self, exc_type, exc, tb):
        super().__exit__(exc_type, exc, tb)
        self.session.close()
        
    def _commit(self):
        self.session.commit()
    
    def rollback(self):
        self.session.rollback()