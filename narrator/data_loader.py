import csv
import json
import logging
import pathlib
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class DataLoader:
    """
    Loads marine ecosystem simulation event data from JSON or CSV files.
    Validates schema and returns a normalized list of event dicts.
    """

    REQUIRED_FIELDS = [
        "timestamp", "event_type", "zone",
        "organism", "count", "severity", "details"
    ]

    VALID_ZONES = {
        "reef_zone_A", "deep_zone_B", "surface_zone",
        "mangrove_edge", "open_water"
    }

    def load(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Load events from a .json or .csv file.
        Raises ValueError if file extension is unsupported.
        Raises FileNotFoundError if the file does not exist.
        Returns a list of validated event dicts.
        """
        path = pathlib.Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Simulation data file not found: {filepath}")

        if path.suffix == ".json":
            events = self._load_json(filepath)
        elif path.suffix == ".csv":
            events = self._load_csv(filepath)
        else:
            raise ValueError(f"Unsupported file extension: {path.suffix}. Use .json or .csv.")

        return self._validate(events)

    def _load_json(self, filepath: str) -> List[Dict[str, Any]]:
        """Load and parse a JSON file into a list of dicts."""
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_csv(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Load a CSV file. Convert empty strings back to None.
        Convert count field from string to int or None.
        """
        events = []
        with open(filepath, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert empty strings to None
                processed_row = {k: (v if v != "" else None) for k, v in row.items()}
                
                # Convert count to int if possible
                if processed_row.get("count") is not None:
                    try:
                        processed_row["count"] = int(processed_row["count"])
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid count format: {processed_row['count']}. Setting to None.")
                        processed_row["count"] = None
                
                events.append(processed_row)
        return events

    def _validate(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate each event dict.
        - Check all REQUIRED_FIELDS are present.
        - Check zone is one of VALID_ZONES.
        - Check count is a non-negative integer or None.
        - Log a warning (do not raise) for invalid zones.
        Returns the original list (validation is non-blocking for warnings).
        """
        for i, event in enumerate(events):
            # Check required fields
            for field in self.REQUIRED_FIELDS:
                if field not in event:
                    raise ValueError(f"Missing required field '{field}' in event index {i}")

            # Check zone validity
            zone = event.get("zone")
            if zone not in self.VALID_ZONES:
                logger.warning(f"Unknown zone detected at index {i}: {zone}")

            # Check count
            count = event.get("count")
            if count is not None:
                if not isinstance(count, int) or count < 0:
                    logger.warning(f"Invalid count at index {i}: {count}. Expected non-negative integer or None.")

        return events

    def summarize(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Return a summary dict with these keys:
        - total_events: int
        - event_types: dict mapping event_type -> count
        - zones_affected: list of unique zone names
        - organisms_involved: list of unique organism names (exclude None)
        - high_severity_count: int
        """
        total_events = len(events)
        event_types = {}
        zones_affected = set()
        organisms_involved = set()
        high_severity_count = 0

        for event in events:
            # Count event types
            etype = event.get("event_type", "unknown")
            event_types[etype] = event_types.get(etype, 0) + 1

            # Track zones
            if event.get("zone"):
                zones_affected.add(event["zone"])

            # Track organisms
            if event.get("organism"):
                organisms_involved.add(event["organism"])

            # Track severity
            if event.get("severity") == "high":
                high_severity_count += 1

        return {
            "total_events": total_events,
            "event_types": event_types,
            "zones_affected": sorted(list(zones_affected)),
            "organisms_involved": sorted(list(organisms_involved)),
            "high_severity_count": high_severity_count
        }
