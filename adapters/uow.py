from abc import ABC, abstractmethod
from adapters import repository
from adapters.repository import SqlAlchemyRepository
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import config

get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))

class AbstractUnitOfWork(ABC):
    products: repository.AbstractRepository
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc, tb):
        self.rollback()
    
    @abstractmethod
    def commit(self):
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
        
    def commit(self):
        self.session.commit()
    
    def rollback(self):
        self.session.rollback()