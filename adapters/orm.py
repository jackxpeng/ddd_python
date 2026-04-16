from sqlalchemy import Table, MetaData, Column, Integer, String, Date
from sqlalchemy.orm import mapper

from domain import model

metadata_obj = MetaData()

batches = Table(
    'batches',
    metadata_obj,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('ref_id', String(255)),
    Column('sku', String(255)),
    Column('qty', Integer, nullable=False),
    Column('eta', Date, nullable=True),
)

def start_mappers():
    mapper(model.Batch, batches)