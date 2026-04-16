from sqlalchemy import Table, MetaData, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import mapper, relationship

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

orderlines = Table(
    'orderlines',
    metadata_obj,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('order_id', String(225)),
    Column('sku', String(225)),
    Column('qty', Integer, nullable=False),
)

allocations = Table(
    'allocations',
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderline_id", ForeignKey("orderlines.id"), unique=True),
    Column('batch_id', ForeignKey("batches.id"))
)

def start_mappers():
    lines_mapper = mapper(model.OrderLine, orderlines)
    mapper(model.Batch, 
           batches,
           properties={
               "allocations": relationship(
                   lines_mapper, secondary=allocations, collection_class=set,
               )
           })