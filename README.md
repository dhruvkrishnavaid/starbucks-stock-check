# Starbucks Stock Check

A small FastAPI service that reads a store stock snapshot CSV and reports which
drink ingredients are sold out, for example oat milk at First Hill.

## What it does

- Loads `data/Store Stock Snapshot, 7 March 2025 06:45.csv` when it starts. The
  file has one row per store per ingredient, with quantity on hand, reserved
  quantity and the time the row was last updated.
- Works out availability for each row as `quantity_on_hand - reserved_quantity`.
- Reports an item as `sold_out` when its availability is 0 or less, and as
  `in_stock` otherwise.
- Treats any item whose `component_id` contains `milk` as a milk. That covers
  `oat_milk`, `almond_milk` and `two_pct_milk` in the snapshot.

## Project layout

```
stock_service/
  snapshot.py   # CSV parsing and availability rules
  app.py        # FastAPI app and routes
data/
  Store Stock Snapshot, 7 March 2025 06:45.csv   # default snapshot
tests/
  test_stock_service.py                          # uses its own small snapshot
requirements.txt
```

## Requirements

- Python 3.9 or newer
- The packages in `requirements.txt` (FastAPI, uvicorn, httpx, pytest)

## Setup

```bash
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

## Run the service

```bash
./.venv/bin/uvicorn stock_service.app:app --host 127.0.0.1 --port 8000
```

The interactive API docs are at http://127.0.0.1:8000/docs.

To use a different snapshot, set `STOCK_SNAPSHOT_PATH` before starting:

```bash
STOCK_SNAPSHOT_PATH="/path/to/another snapshot.csv" ./.venv/bin/uvicorn stock_service.app:app --port 8000
```

## Endpoints

| Method | Path | Returns |
| --- | --- | --- |
| GET | `/health` | Service status and the snapshot file in use |
| GET | `/stores/{store_id}/milks` | Every milk at the store, with its status |
| GET | `/stores/{store_id}/items/{component_id}` | One item at the store, with its status |

Store IDs in the snapshot are: `10482` (First Hill - Madison & Boylston),
`11307` (Capitol Hill - Broadway & Pine) and `09815` (South Lake Union -
Westlake & Mercer).

Unknown stores or items return `404`.

### Example

```bash
curl -s http://127.0.0.1:8000/stores/10482/milks
```

For First Hill this lists:

| Milk | Status | On hand | Reserved | Available |
| --- | --- | --- | --- | --- |
| Oatmilk | sold out | 0 | 0 | 0 |
| Almondmilk | in stock | 38 | 1 | 37 |
| 2% Milk | in stock | 96 | 3 | 93 |

```bash
curl -s http://127.0.0.1:8000/stores/10482/items/oat_milk
```

## Tests

```bash
./.venv/bin/python -m pytest -q
```

The tests build a small snapshot in a temporary folder, so they don't depend
on the file in `data/`.

## Notes

- The service reads the snapshot once at startup. Restart it to pick up a
  changed file.
- The `store_open` flag is returned with each item but does not change the
  status. A closed store still reports its stock as it is in the file.
