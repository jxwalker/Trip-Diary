import pytest
from unittest.mock import Mock, patch
from src.gpt_providers.claude_gpt import ClaudeGPT

@patch('src.gpt_providers.claude_gpt.Anthropic')
def test_claude_gpt_generate_text(mock_anthropic):
    """Test Claude GPT text generation."""
    # Create a message response that matches Claude's API structure
    message = Mock()
    message.content = "Test Response"  # Claude API returns content directly
    
    # Set up the client
    mock_client = Mock()
    mock_client.messages.create.return_value = message
    mock_anthropic.return_value = mock_client
    
    # Create instance and test
    claude_gpt = ClaudeGPT()
    response = claude_gpt.generate_text("Test prompt", "Test system")
    
    # Verify response
    assert response == "Test Response"
    
    # Verify the correct messages were sent
    mock_client.messages.create.assert_called_once_with(
        model="claude-3-sonnet-20240229",
        max_tokens=4000,
        temperature=0,
        messages=[
            {"role": "system", "content": "Test system"},
            {"role": "user", "content": "Test prompt"}
        ]
    )
