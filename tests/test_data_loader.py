import pytest
import json
import csv
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock
from narrator.data_loader import DataLoader

def test_load_json_returns_list_of_dicts(tmp_path):
    d = tmp_path / "data"
    d.mkdir()
    f = d / "test.json"
    data = [{"timestamp": "2026-03-28T08:00:00Z", "event_type": "spawn", "zone": "reef_zone_A", 
             "organism": "clownfish", "count": 10, "severity": "low", "details": "test"}]
    f.write_text(json.dumps(data))
    
    loader = DataLoader()
    events = loader.load(str(f))
    assert isinstance(events, list)
    assert isinstance(events[0], dict)
    assert events[0]["organism"] == "clownfish"

def test_load_csv_returns_list_of_dicts(tmp_path):
    d = tmp_path / "data"
    d.mkdir()
    f = d / "test.csv"
    f.write_text("timestamp,event_type,zone,organism,count,severity,details\n2026-03-28T08:00:00Z,spawn,reef_zone_A,clownfish,10,low,test")
    
    loader = DataLoader()
    events = loader.load(str(f))
    assert isinstance(events, list)
    assert events[0]["count"] == 10

def test_load_raises_file_not_found():
    loader = DataLoader()
    with pytest.raises(FileNotFoundError):
        loader.load("non_existent_file.json")

def test_load_raises_value_error_for_unsupported_extension(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("not a json or csv")
    loader = DataLoader()
    with pytest.raises(ValueError, match="Unsupported file extension"):
        loader.load(str(f))

def test_load_csv_count_is_none_for_missing(tmp_path):
    f = tmp_path / "test.csv"
    # Missing count (empty string)
    f.write_text("timestamp,event_type,zone,organism,count,severity,details\n2026-03-28T08:00:00Z,spawn,reef_zone_A,clownfish,,low,test")
    
    loader = DataLoader()
    events = loader.load(str(f))
    assert events[0]["count"] is None

@patch("narrator.data_loader.logger")
def test_validate_warns_on_invalid_zone(mock_logger):
    loader = DataLoader()
    events = [{
        "timestamp": "2026-03-28T08:00:00Z",
        "event_type": "spawn",
        "zone": "invalid_zone",
        "organism": "fish",
        "count": 1,
        "severity": "low",
        "details": "test"
    }]
    loader._validate(events)
    mock_logger.warning.assert_called_with("Unknown zone detected at index 0: invalid_zone")

def test_summarize_returns_correct_total():
    loader = DataLoader()
    events = [
        {"event_type": "A", "zone": "Z1", "organism": "O1", "severity": "low"},
        {"event_type": "B", "zone": "Z2", "organism": "O2", "severity": "high"}
    ]
    summary = loader.summarize(events)
    assert summary["total_events"] == 2
    assert summary["high_severity_count"] == 1

def test_summarize_event_types_are_counted():
    loader = DataLoader()
    events = [
        {"event_type": "spawn"},
        {"event_type": "spawn"},
        {"event_type": "death"}
    ]
    summary = loader.summarize(events)
    assert summary["event_types"]["spawn"] == 2
    assert summary["event_types"]["death"] == 1

def test_summarize_excludes_none_organisms():
    loader = DataLoader()
    events = [
        {"organism": "clownfish"},
        {"organism": None},
        {"organism": "shark"}
    ]
    summary = loader.summarize(events)
    assert "clownfish" in summary["organisms_involved"]
    assert "shark" in summary["organisms_involved"]
    assert None not in summary["organisms_involved"]
    assert len(summary["organisms_involved"]) == 2

def test_load_json_count_matches_expected():
    loader = DataLoader()
    # Using the real sample file created earlier
    events = loader._load_json("data/sample_events.json")
    assert len(events) == 12
