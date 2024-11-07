import pytest
from unittest.mock import Mock
from src.gpt_providers.claude_gpt import ClaudeGPT

@pytest.fixture
def mock_anthropic(monkeypatch):
    # Create a mock client
    mock_client = Mock()
    # Create a mock for the messages.create method
    mock_messages = Mock()
    mock_messages.create.return_value = Mock(content="Test response")
    mock_client.messages = mock_messages
    
    # Ensure the ClaudeGPT instance uses the mocked client
    monkeypatch.setattr("src.gpt_providers.claude_gpt.ClaudeGPT", lambda: Mock(client=mock_client))
    return mock_client

def test_claude_gpt_generate_text(mock_anthropic):
    # Create an instance of ClaudeGPT
    claude_gpt = ClaudeGPT()
    # Call the generate_text method
    response = claude_gpt.generate_text("Respond to this Test prompt with the words Test response", "Test system")
    
    # Assert that the response is as expected
    assert response == "Test response"
