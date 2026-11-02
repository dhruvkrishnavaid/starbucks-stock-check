from __future__ import annotations

import os
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from stock_service.snapshot import Snapshot, StockRow

DEFAULT_SNAPSHOT_PATH = Path(
    "/Users/dhruv/Documents/Store Stock Snapshot, 7 March 2025 06:45.csv"
)


class ItemStatus(BaseModel):
    store_id: str
    store_name: str
    store_open: bool
    component_id: str
    component_name: str
    quantity_on_hand: int
    reserved_quantity: int
    available: int
    status: str
    last_updated_at: str


def _status(row: StockRow) -> ItemStatus:
    return ItemStatus(
        store_id=row.store_id,
        store_name=row.store_name,
        store_open=row.store_open,
        component_id=row.component_id,
        component_name=row.component_name,
        quantity_on_hand=row.quantity_on_hand,
        reserved_quantity=row.reserved_quantity,
        available=row.available,
        status="sold_out" if row.sold_out else "in_stock",
        last_updated_at=row.last_updated_at,
    )


class MilkList(BaseModel):
    store_id: str
    store_name: str
    milks: List[ItemStatus]


def create_app(snapshot_path: Path) -> FastAPI:
    snapshot = Snapshot.load(snapshot_path)
    app = FastAPI(title="Starbucks Stock Service")

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "snapshot": str(snapshot_path)}

    @app.get("/stores/{store_id}/milks", response_model=MilkList)
    def store_milks(store_id: str) -> MilkList:
        rows = snapshot.store_rows(store_id)
        if not rows:
            raise HTTPException(status_code=404, detail=f"Unknown store {store_id}")
        return MilkList(
            store_id=store_id,
            store_name=rows[0].store_name,
            milks=[_status(row) for row in snapshot.milks(store_id)],
        )

    @app.get("/stores/{store_id}/items/{component_id}", response_model=ItemStatus)
    def store_item(store_id: str, component_id: str) -> ItemStatus:
        row = snapshot.item(store_id, component_id)
        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"No item {component_id} for store {store_id}",
            )
        return _status(row)

    return app


app = create_app(Path(os.environ.get("STOCK_SNAPSHOT_PATH", DEFAULT_SNAPSHOT_PATH)))
