from abc import ABC, abstractmethod

from domain.model import Batch

class AbstractRepository(ABC):
    @abstractmethod
    def add(self, batch: Batch):
        raise NotImplementedError

    @abstractmethod
    def get(self, ref_id: str) -> Batch | None:
        raise NotImplementedError

    @abstractmethod
    def list(self):
        raise NotImplementedError

class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session
    
    def add(self, batch: Batch):
        self.session.add(batch)
    
    def get(self, ref_id: str) -> Batch | None:
        return self.session.query(Batch).filter_by(ref_id=ref_id).first()

    def list(self):
        return self.session.query(Batch).all()
    
