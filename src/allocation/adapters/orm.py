from sqlalchemy import Table, MetaData, Column, Integer, String, Date, ForeignKey, event
from sqlalchemy.orm import registry, relationship

from allocation.domain import model

metadata_obj = MetaData()


products = Table(
    "products",
    metadata_obj,
    Column("sku", String(255), primary_key=True),
    Column("version_number", Integer, nullable=False, server_default="0"),
)

batches = Table(
    "batches",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("ref_id", String(255)),
    Column("sku", ForeignKey("products.sku")),
    Column("qty", Integer, nullable=False),
    Column("eta", Date, nullable=True),
)

orderlines = Table(
    "orderlines",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("order_id", String(225)),
    Column("sku", String(225)),
    Column("qty", Integer, nullable=False),
)

allocations = Table(
    "allocations",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderline_id", ForeignKey("orderlines.id"), unique=True),
    Column("batch_id", ForeignKey("batches.id")),
)


allocations_view = Table(
    "allocations_view",
    metadata_obj,
    Column("order_id", String(255)),
    Column("sku", String(255)),
    Column("batch_ref", String(255)),
)


mapper_registry = registry()


def start_mappers():
    lines_mapper = mapper_registry.map_imperatively(model.OrderLine, orderlines)
    batches_mapper = mapper_registry.map_imperatively(
        model.Batch,
        batches,
        properties={
            "allocations": relationship(
                lines_mapper,
                secondary=allocations,
                collection_class=set,
            )
        },
    )
    mapper_registry.map_imperatively(
        model.Product, products, properties={"batches": relationship(batches_mapper)}
    )


@event.listens_for(model.Product, "load")
def receive_load(product, _):
    product.events = []
