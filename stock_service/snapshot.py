from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass(frozen=True)
class StockRow:
    store_id: str
    store_name: str
    store_open: bool
    component_id: str
    component_name: str
    component_type: str
    quantity_on_hand: int
    reserved_quantity: int
    last_updated_at: str

    @property
    def available(self) -> int:
        return self.quantity_on_hand - self.reserved_quantity

    @property
    def sold_out(self) -> bool:
        return self.available <= 0


def _parse_row(raw: Dict[str, str]) -> StockRow:
    return StockRow(
        store_id=raw["store_id"].strip(),
        store_name=raw["store_name"].strip(),
        store_open=raw["store_open"].strip().lower() == "true",
        component_id=raw["component_id"].strip(),
        component_name=raw["component_name"].strip(),
        component_type=raw["component_type"].strip(),
        quantity_on_hand=int(raw["quantity_on_hand"]),
        reserved_quantity=int(raw["reserved_quantity"]),
        last_updated_at=raw["last_updated_at"].strip(),
    )


class Snapshot:
    """In-memory view of a store stock snapshot CSV."""

    def __init__(self, rows: List[StockRow]) -> None:
        self._rows = rows

    @classmethod
    def load(cls, path: Path) -> "Snapshot":
        with path.open(newline="", encoding="utf-8") as handle:
            return cls([_parse_row(row) for row in csv.DictReader(handle)])

    def store_rows(self, store_id: str) -> List[StockRow]:
        return [row for row in self._rows if row.store_id == store_id]

    def item(self, store_id: str, component_id: str) -> Optional[StockRow]:
        for row in self.store_rows(store_id):
            if row.component_id == component_id:
                return row
        return None

    def milks(self, store_id: str) -> List[StockRow]:
        return [row for row in self.store_rows(store_id) if "milk" in row.component_id]
