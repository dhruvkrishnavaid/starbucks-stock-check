import csv

from fastapi.testclient import TestClient

from stock_service.app import DEFAULT_SNAPSHOT_PATH, create_app

FIRST_HILL_ID = "10482"


def _first_hill_rows() -> list:
    with DEFAULT_SNAPSHOT_PATH.open(newline="", encoding="utf-8") as handle:
        return [row for row in csv.DictReader(handle) if row["store_id"] == FIRST_HILL_ID]


def test_every_first_hill_row_matches_snapshot_availability() -> None:
    client = TestClient(create_app(DEFAULT_SNAPSHOT_PATH))
    rows = _first_hill_rows()
    assert len(rows) == 10

    for row in rows:
        on_hand = int(row["quantity_on_hand"])
        reserved = int(row["reserved_quantity"])
        expected_available = on_hand - reserved
        expected_status = "sold_out" if expected_available <= 0 else "in_stock"

        body = client.get(f"/stores/{FIRST_HILL_ID}/items/{row['component_id']}").json()

        assert body["available"] == expected_available, row["component_id"]
        assert body["status"] == expected_status, row["component_id"]


def test_first_hill_oat_milk_is_the_only_sold_out_item() -> None:
    client = TestClient(create_app(DEFAULT_SNAPSHOT_PATH))
    statuses = {
        row["component_id"]: client.get(
            f"/stores/{FIRST_HILL_ID}/items/{row['component_id']}"
        ).json()["status"]
        for row in _first_hill_rows()
    }

    sold_out = [component for component, status in statuses.items() if status == "sold_out"]
    assert sold_out == ["oat_milk"]
