import os
import pytest
from unittest.mock import patch, MagicMock
from narrator.ai_client import AIClient, MOCK_NARRATION

def test_client_is_mock_when_no_api_key():
    with patch.dict(os.environ, {}, clear=True):
        client = AIClient()
        assert client.is_mock is True
        assert client.mode == "MOCK"

def test_client_is_live_when_api_key_set():
    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"}, clear=True):
        client = AIClient()
        assert client.is_mock is False
        assert client.mode == "GEMINI"

def test_client_is_openrouter_when_openrouter_key_set():
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-fake"}, clear=True):
        client = AIClient()
        assert client.is_mock is False
        assert client.mode == "OPENROUTER"

def test_generate_returns_mock_narration_in_mock_mode():
    with patch.dict(os.environ, {}, clear=True):
        client = AIClient(force_mock=True)
        narration = client.generate("test prompt")
        assert narration == MOCK_NARRATION

def test_generate_mock_narration_is_nonempty_string():
    with patch.dict(os.environ, {}, clear=True):
        client = AIClient(force_mock=True)
        narration = client.generate("test prompt")
        assert isinstance(narration, str)
        assert len(narration) > 50

@patch("narrator.ai_client.AIClient._call_gemini")
def test_generate_calls_gemini_when_key_present(mock_call):
    mock_call.return_value = "Gemini response"
    # Explicitly clear OpenRouter key to ensure Gemini is picked
    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key", "OPENROUTER_API_KEY": ""}, clear=True):
        client = AIClient()
        result = client.generate("test")
        assert result == "Gemini response"
        mock_call.assert_called_once()

@patch("narrator.ai_client.AIClient._call_openrouter")
def test_generate_calls_openrouter_when_key_present(mock_call):
    mock_call.return_value = "OpenRouter response"
    # OpenRouter is prioritized, but let's be safe
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-fake", "GEMINI_API_KEY": ""}, clear=True):
        client = AIClient()
        result = client.generate("test")
        assert result == "OpenRouter response"
        mock_call.assert_called_once()

def test_generate_raises_runtime_error_on_api_failure():
    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"}, clear=True):
        client = AIClient()
        with patch.object(client, "_call_gemini", side_effect=Exception("API Error")):
            with pytest.raises(RuntimeError, match="API call failed"):
                client.generate("test")

def test_mode_property_returns_mock():
    with patch.dict(os.environ, {}, clear=True):
        client = AIClient(force_mock=True)
        assert client.mode == "MOCK"
