import pytest
import logging
from unittest.mock import patch
from narrator.formatter import OutputFormatter

def test_format_returns_string():
    f = OutputFormatter()
    output = f.format("Test narration.", "MOCK", {"total_events": 1})
    assert isinstance(output, str)
    assert "MARINE ECOSYSTEM NARRATION" in output

def test_format_contains_narration_text():
    f = OutputFormatter()
    narration = "A rare sighting of a blue whale was recorded today."
    output = f.format(narration, "LIVE", {"total_events": 1})
    assert "blue whale" in output

def test_format_contains_mode_mock():
    f = OutputFormatter()
    output = f.format("test", "MOCK", {})
    assert "[MOCK]" in output

def test_format_contains_mode_live():
    f = OutputFormatter()
    output = f.format("test", "LIVE", {})
    assert "[LIVE]" in output

def test_clean_strips_extra_whitespace():
    f = OutputFormatter()
    raw = "  This   is    messy.  \n\n"
    clean = f.clean(raw)
    assert clean == "This is messy."

def test_clean_adds_period_if_missing():
    f = OutputFormatter()
    assert f.clean("No period") == "No period."
    assert f.clean("Has period.") == "Has period."

def test_count_sentences_returns_correct_count():
    f = OutputFormatter()
    assert f.count_sentences("Sentence one. Sentence two? Sentence three!") == 3
    assert f.count_sentences("Single sentence.") == 1

def test_count_sentences_handles_single_sentence():
    f = OutputFormatter()
    assert f.count_sentences("One sentence") == 1

@patch("narrator.formatter.logger")
def test_warn_if_out_of_range_logs_warning_for_one_sentence(mock_logger):
    f = OutputFormatter()
    f.warn_if_out_of_range("Only one sentence.")
    mock_logger.warning.assert_called()

@patch("narrator.formatter.logger")
def test_warn_if_out_of_range_no_warning_for_three_sentences(mock_logger):
    f = OutputFormatter()
    f.warn_if_out_of_range("One. Two. Three.")
    mock_logger.warning.assert_not_called()
