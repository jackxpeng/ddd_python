import requests


def test_happy_path_returns_201_and_allocated_batch(api_url, add_stock):
    sku, othersku = "DESK", "CHAIR"
    earlybatch = "batch-01"
    laterbatch = "batch-02"
    otherbatch = "batch-03"

    # 1. Setup: Use the fixture to hide the raw SQL!
    add_stock(
        [
            (laterbatch, sku, 100, "2026-05-02"),
            (earlybatch, sku, 100, "2026-05-01"),
            (otherbatch, othersku, 100, None),
        ]
    )

    response = requests.post(
        f"{api_url}/allocate", json={"orderid": "order-123", "sku": sku, "qty": 10}
    )
    assert response.status_code == 201
    assert response.json()["batchref"] == earlybatch


def test_unhappy_path_returns_400_and_allocate_batch_invalid_sku(api_url, add_stock):
    sku, othersku, no_such_sku = "DESK", "CHAIR", "UNICORN"
    earlybatch = "batch-01"
    laterbatch = "batch-02"
    otherbatch = "batch-03"

    # 1. Setup: Use the fixture to hide the raw SQL!
    add_stock(
        [
            (laterbatch, sku, 100, "2026-05-02"),
            (earlybatch, sku, 100, "2026-05-01"),
            (otherbatch, othersku, 100, None),
        ]
    )

    response = requests.post(
        f"{api_url}/allocate",
        json={"orderid": "order-123", "sku": no_such_sku, "qty": 10},
    )
    assert response.status_code == 400
    assert response.json()["message"] == f"Invalid sku: {no_such_sku}"
