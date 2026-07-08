from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from conduit.core.ports import Cursor, RawItem
from conduit.core.task import SourceRef


class FileSource:
    """Reads .txt files from an inbox directory.

    Files whose mtime is strictly after `since` are returned (or all files
    when `since` is None). This mirrors how cursor-based incremental fetching
    will work for automated sources like reMarkable sync.
    """

    def __init__(self, inbox_dir: Path, source_id: str = "file") -> None:
        self.id = source_id
        self._inbox = inbox_dir
        self._inbox.mkdir(parents=True, exist_ok=True)

    def fetch(self, since: Cursor) -> list[RawItem]:
        items: list[RawItem] = []
        for path in sorted(self._inbox.glob("*.txt")):
            mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
            if since is not None and mtime <= since:
                continue
            text = path.read_text(encoding="utf-8").strip()
            if not text:
                continue
            ref = SourceRef(
                source_id=self.id,
                item_ref=path.name,
                fetched_at=mtime,
                triggering_statement=text[:200],  # overwritten by _promote later
            )
            items.append(RawItem(source_ref=ref, text=text))
        return items
