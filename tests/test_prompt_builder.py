import pytest
from narrator.prompt_builder import PromptBuilder

def test_build_returns_string():
    builder = PromptBuilder()
    events = [{"event_type": "spawn", "zone": "reef_zone_A", "organism": "clownfish", "count": 10, "details": "test"}]
    summary = {"total_events": 1, "event_types": {"spawn": 1}, "zones_affected": ["reef_zone_A"], "organisms_involved": ["clownfish"], "high_severity_count": 0}
    prompt = builder.build(events, summary)
    assert isinstance(prompt, str)
    assert len(prompt) > 100

def test_build_contains_system_context():
    builder = PromptBuilder()
    prompt = builder.build([], {})
    assert "MarineNarrator" in prompt
    assert "2 to 4 sentences" in prompt

def test_build_contains_narration_instruction():
    builder = PromptBuilder()
    prompt = builder.build([], {})
    assert "Based on the simulation events above, write a 2-4 sentence" in prompt

def test_build_contains_all_event_types():
    builder = PromptBuilder()
    events = [
        {"event_type": "plankton_bloom", "zone": "surface_zone", "organism": "phytoplankton", "count": 100, "details": "test"},
        {"event_type": "predator_movement", "zone": "open_water", "organism": "shark", "count": 1, "details": "test"}
    ]
    summary = {"total_events": 2, "event_types": {"plankton_bloom": 1, "predator_movement": 1}, "zones_affected": ["surface_zone", "open_water"], "organisms_involved": ["phytoplankton", "shark"], "high_severity_count": 0}
    prompt = builder.build(events, summary)
    assert "PLANKTON_BLOOM" in prompt
    assert "PREDATOR_MOVEMENT" in prompt

def test_build_contains_zone_names():
    builder = PromptBuilder()
    events = [{"zone": "reef_zone_A", "event_type": "spawn"}]
    summary = {"zones_affected": ["reef_zone_A"]}
    prompt = builder.build(events, summary)
    assert "reef_zone_A" in prompt

def test_format_event_line_includes_timestamp():
    builder = PromptBuilder()
    event = {"timestamp": "2026-03-28T08:00:00Z", "event_type": "spawn", "zone": "reef_zone_A", "organism": "clownfish", "count": 10, "details": "test"}
    line = builder._format_event_line(event)
    assert "[08:00 UTC]" in line

def test_format_event_line_handles_null_organism():
    builder = PromptBuilder()
    event = {"timestamp": "2026-03-28T09:00:00Z", "event_type": "temp", "zone": "reef_zone_A", "organism": None, "count": None, "details": "test"}
    line = builder._format_event_line(event)
    assert "N/A" in line
    assert "TEMP" in line

def test_format_summary_block_shows_total_events():
    builder = PromptBuilder()
    summary = {"total_events": 12, "event_types": {"A": 5, "B": 7}, "zones_affected": ["Z1"], "organisms_involved": ["O1"], "high_severity_count": 2}
    block = builder._format_summary_block(summary)
    assert "Total events : 12" in block
    assert "High severity: 2 events" in block

def test_build_prompt_length_is_reasonable():
    builder = PromptBuilder()
    events = [{"event_type": "A", "zone": "Z", "organism": "O", "count": 1, "details": "test"}]
    summary = {"total_events": 1}
    prompt = builder.build(events, summary)
    # Context (~500 chars) + event + summary
    assert len(prompt) > 400
