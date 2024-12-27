import pytest
import os
from unittest.mock import Mock, patch
from services.version_control import VersionControlService

@pytest.fixture
def version_control():
    with patch('services.version_control.git') as mock_git:
        service = VersionControlService(base_path='/tmp/test_repos')
        yield service

def test_init_user_repo(version_control):
    # Arrange
    user_id = "test_user_123"
    
    # Act
    result = version_control.init_user_repo(user_id)
    
    # Assert
    assert result["status"] == "success"
    assert "repo_path" in result

def test_save_note_version(version_control):
    # Arrange
    user_id = "test_user_123"
    note_id = "note_123"
    content = {"title": "Test Note", "content": "Test content"}
    
    # Act
    result = version_control.save_note_version(user_id, note_id, content)
    
    # Assert
    assert result["status"] == "success"
    assert "commit_hash" in result

def test_get_note_history(version_control):
    # Arrange
    user_id = "test_user_123"
    note_id = "note_123"
    mock_commit = Mock()
    mock_commit.hexsha = "abc123"
    mock_commit.committed_date = 1640995200
    mock_commit.message = "Update note"
    version_control.repo.iter_commits.return_value = [mock_commit]
    
    # Act
    history = version_control.get_note_history(user_id, note_id)
    
    # Assert
    assert isinstance(history, list)
    assert len(history) > 0
    assert "commit_hash" in history[0]
    assert "timestamp" in history[0]
    assert "message" in history[0]

def test_restore_note_version(version_control):
    # Arrange
    user_id = "test_user_123"
    note_id = "note_123"
    commit_hash = "abc123"
    
    # Act
    result = version_control.restore_note_version(user_id, note_id, commit_hash)
    
    # Assert
    assert result["status"] == "success"
    assert "content" in result

def test_create_branch(version_control):
    # Arrange
    user_id = "test_user_123"
    branch_name = "feature/test"
    
    # Act
    result = version_control.create_branch(user_id, branch_name)
    
    # Assert
    assert result["status"] == "success"
    assert "branch_name" in result

def test_merge_branch(version_control):
    # Arrange
    user_id = "test_user_123"
    source_branch = "feature/test"
    target_branch = "main"
    
    # Act
    result = version_control.merge_branch(user_id, source_branch, target_branch)
    
    # Assert
    assert result["status"] == "success"
    assert "merge_commit" in result
