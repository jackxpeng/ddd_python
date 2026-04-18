from sqlalchemy import text

from domain.model import OrderLine, Batch


def test_can_load_orderlines(session):
    order01 = OrderLine(order_id="order01", sku="CHAIR", qty=100)
    order02 = OrderLine(order_id="order01", sku="DESK", qty=10)
    session.execute(
        text(
            "INSERT INTO orderlines (order_id, sku, qty) VALUES "
            f"('{order01.order_id}', '{order01.sku}', {order01.qty}),"
            f"('{order02.order_id}', '{order02.sku}', {order02.qty})"
        )
    )
    expected = [order01, order02]
    orderlines_read = session.query(OrderLine).all()

    assert expected == orderlines_read


def test_can_save_orderlines(session):
    order01 = OrderLine(order_id="order01", sku="CHAIR", qty=100)
    session.add(order01)
    session.commit()
    expected = [(order01.order_id, order01.sku, order01.qty)]
    orderlines_read = list(
        session.execute(text("SELECT order_id, sku, qty FROM orderlines"))
    )
    assert expected == orderlines_read


def test_can_save_allocations(session):
    batch01 = Batch("batch01", "CHAIR", 10)
    order01 = OrderLine("order01", "CHAIR", 1)
    assert batch01.allocate(order01)
    session.add(batch01)
    session.add(order01)
    session.commit()
    order_allocated_read = list(session.execute(
        text(
            "SELECT o.order_id, o.sku, o.qty FROM batches b "
            "inner join allocations a ON b.id = a.batch_id "
            "INNER JOIN orderlines o ON o.id = a.orderline_id "
            "WHERE b.ref_id = 'batch01' "
            )))

    expected = [(order01.order_id, order01.sku, order01.qty)]
    assert expected == order_allocated_read
