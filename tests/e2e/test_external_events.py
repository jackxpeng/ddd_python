import json
import requests
from tenacity import Retrying, stop_after_delay

# from . import redis_client


def test_change_batch_quantity_leading_to_reallocation(
    api_url, add_stock, subscribe_to_redis, publish_to_redis
):
    orderid, sku = "order-123", "E2E-OAK-DESK"
    earlier_batch, later_batch = "batch-old", "batch-newer"

    add_stock(
        [
            (earlier_batch, sku, 10, "2026-01-01"),
            (later_batch, sku, 10, "2026-01-02"),
        ]
    )

    # Allocate the order via the API
    response = requests.post(
        f"{api_url}/allocate", json={"orderid": orderid, "sku": sku, "qty": 10}
    )
    assert response.status_code == 202

    # 2. Subscribe to the outbound Redis channel
    subscription = subscribe_to_redis("line_allocated")

    # 3. Change quantity on allocated batch so it's less than our order
    # Note: Using "ref" to match what your redis_eventconsumer.py expects!
    publish_to_redis(
        "change_batch_quantity",
        {"ref": earlier_batch, "qty": 5},
    )

    # 4. Wait until we see a message saying the order has been reallocated
    messages = []
    for attempt in Retrying(stop=stop_after_delay(3), reraise=True):
        with attempt:
            message = subscription.get_message(timeout=1)
            if message:
                messages.append(message)

            assert messages, "No messages received from Redis yet"

            data = json.loads(messages[-1]["data"])
            # Note: Using "order_id" to match your events.Allocated dataclass
            assert data["order_id"] == orderid
            assert data["batchref"] == later_batch
