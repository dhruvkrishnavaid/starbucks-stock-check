from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from stock_service.app import create_app

HEADER = (
    "store_id,store_name,store_open,component_id,component_name,component_type,"
    "quantity_on_hand,reserved_quantity,last_updated_at\n"
)

ROWS = [
    "10482,First Hill - Madison & Boylston,true,oat_milk,Oatmilk,drink_base,0,0,2025-03-07T06:35:00-08:00",
    "10482,First Hill - Madison & Boylston,true,almond_milk,Almondmilk,drink_base,38,1,2025-03-07T06:41:05-08:00",
    "10482,First Hill - Madison & Boylston,true,two_pct_milk,2% Milk,drink_base,96,3,2025-03-07T06:43:40-08:00",
    "10482,First Hill - Madison & Boylston,true,cups_ice,Cups & Ice,drink_base,176,6,2025-03-07T06:44:12-08:00",
    "11307,Capitol Hill - Broadway & Pine,true,oat_milk,Oatmilk,drink_base,2,1,2025-03-07T06:44:02-08:00",
]


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    snapshot = tmp_path / "snapshot.csv"
    snapshot.write_text(HEADER + "\n".join(ROWS) + "\n", encoding="utf-8")
    return TestClient(create_app(snapshot))


def test_oat_milk_at_first_hill_is_sold_out(client: TestClient) -> None:
    response = client.get("/stores/10482/items/oat_milk")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "sold_out"
    assert body["available"] == 0


def test_milks_list_only_milk_items_with_status(client: TestClient) -> None:
    response = client.get("/stores/10482/milks")

    assert response.status_code == 200
    body = response.json()
    assert body["store_name"] == "First Hill - Madison & Boylston"
    statuses = {milk["component_id"]: milk["status"] for milk in body["milks"]}
    assert statuses == {
        "oat_milk": "sold_out",
        "almond_milk": "in_stock",
        "two_pct_milk": "in_stock",
    }


def test_available_subtracts_reserved_quantity(client: TestClient) -> None:
    body = client.get("/stores/10482/items/two_pct_milk").json()

    assert body["available"] == 93
    assert body["status"] == "in_stock"


def test_one_unreserved_unit_left_is_still_in_stock(client: TestClient) -> None:
    body = client.get("/stores/11307/items/oat_milk").json()

    assert body["quantity_on_hand"] == 2
    assert body["reserved_quantity"] == 1
    assert body["status"] == "in_stock"


def test_unknown_store_returns_404(client: TestClient) -> None:
    assert client.get("/stores/99999/milks").status_code == 404


def test_unknown_item_returns_404(client: TestClient) -> None:
    assert client.get("/stores/10482/items/soy_milk").status_code == 404
