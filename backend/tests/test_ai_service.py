import pytest
from unittest.mock import Mock, patch
from services.ai_service import AIService

@pytest.fixture
def ai_service():
    return AIService()

@pytest.fixture
def mock_openai():
    with patch('services.ai_service.openai') as mock:
        yield mock

def test_summarize_note(ai_service, mock_openai):
    # Arrange
    test_content = "This is a test note content that needs to be summarized."
    mock_response = Mock()
    mock_response.choices = [Mock(text="Test summary")]
    mock_openai.Completion.create.return_value = mock_response

    # Act
    summary = ai_service.summarize_note(test_content, max_length=50)

    # Assert
    assert summary is not None
    assert isinstance(summary, str)
    mock_openai.Completion.create.assert_called_once()

def test_explain_code(ai_service, mock_openai):
    # Arrange
    test_code = "def hello(): print('Hello, World!')"
    test_language = "python"
    mock_response = Mock()
    mock_response.choices = [Mock(text="Test explanation")]
    mock_openai.Completion.create.return_value = mock_response

    # Act
    explanation = ai_service.explain_code(test_code, test_language)

    # Assert
    assert explanation is not None
    assert isinstance(explanation, dict)
    assert "explanation" in explanation
    mock_openai.Completion.create.assert_called_once()

def test_suggest_improvements(ai_service, mock_openai):
    # Arrange
    test_code = "def hello(): print('Hello, World!')"
    test_language = "python"
    mock_response = Mock()
    mock_response.choices = [Mock(text="Test suggestions")]
    mock_openai.Completion.create.return_value = mock_response

    # Act
    suggestions = ai_service.suggest_improvements(test_code, test_language)

    # Assert
    assert suggestions is not None
    assert isinstance(suggestions, dict)
    assert "suggestions" in suggestions
    mock_openai.Completion.create.assert_called_once()

def test_generate_study_questions(ai_service, mock_openai):
    # Arrange
    test_content = "Python is a programming language."
    mock_response = Mock()
    mock_response.choices = [Mock(text="Q1: What is Python?")]
    mock_openai.Completion.create.return_value = mock_response

    # Act
    questions = ai_service.generate_study_questions(test_content)

    # Assert
    assert questions is not None
    assert isinstance(questions, list)
    assert len(questions) > 0
    mock_openai.Completion.create.assert_called_once()
