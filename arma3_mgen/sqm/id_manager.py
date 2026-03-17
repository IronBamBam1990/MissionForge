"""Centralized ID management for SQM entity and marker IDs."""


class IDManager:
    """Assigns sequential IDs to SQM entities (units, groups, vehicles, etc.) and markers."""

    def __init__(self):
        self._next_id = 0
        self._next_marker_id = 0

    def next_id(self) -> int:
        current = self._next_id
        self._next_id += 1
        return current

    def next_marker_id(self) -> int:
        current = self._next_marker_id
        self._next_marker_id += 1
        return current

    @property
    def total_ids(self) -> int:
        return self._next_id

    @property
    def total_marker_ids(self) -> int:
        return self._next_marker_id
