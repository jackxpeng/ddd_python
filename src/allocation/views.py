from sqlalchemy.orm import Session

def allocations(order_id: str, session: Session):
    results = session.execute(
        """
        SELECT sku, batch_ref AS batchref FROM allocations_view WHERE order_id = :order_id
        """,
        dict(order_id=order_id),
    )
    # Using ._mapping ensures compatibility with newer SQLAlchemy versions
    return [dict(r._mapping) for r in results] 