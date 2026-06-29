"""Tests for pipeline utility functions."""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from pipeline.utils import write_artifact, load_artifact, get_artifact_path, artifact_exists, list_artifacts


@pytest.fixture
def temp_artifacts_dir():
    """Create a temporary artifacts directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("pipeline.utils.ARTIFACTS_DIR", Path(tmpdir)):
            yield Path(tmpdir)


def test_get_artifact_path(temp_artifacts_dir):
    """Test artifact path generation."""
    path = get_artifact_path("test-program", "test.json")
    assert path.parent.name == "test-program"
    assert path.name == "test.json"
    assert path.parent.exists()  # Directory should be created


def test_write_artifact_json(temp_artifacts_dir):
    """Test writing JSON artifact."""
    data = {"test": "data", "nested": {"key": "value"}}
    write_artifact("test-program", "test.json", data)

    path = get_artifact_path("test-program", "test.json")
    assert path.exists()

    with open(path) as f:
        loaded = json.load(f)
    assert loaded == data


def test_write_artifact_markdown(temp_artifacts_dir):
    """Test writing Markdown artifact."""
    content = "# Test Header\n\nSome content here."
    write_artifact("test-program", "test.md", content)

    path = get_artifact_path("test-program", "test.md")
    assert path.exists()

    with open(path) as f:
        loaded = f.read()
    assert loaded == content


def test_load_artifact_json(temp_artifacts_dir):
    """Test loading JSON artifact."""
    data = {"test": "data"}
    write_artifact("test-program", "test.json", data)

    loaded = load_artifact("test-program", "test.json")
    assert loaded == data


def test_load_artifact_markdown(temp_artifacts_dir):
    """Test loading Markdown artifact."""
    content = "# Test"
    write_artifact("test-program", "test.md", content)

    loaded = load_artifact("test-program", "test.md")
    assert loaded == content


def test_load_nonexistent_artifact(temp_artifacts_dir):
    """Test loading a non-existent artifact raises error."""
    with pytest.raises(FileNotFoundError):
        load_artifact("nonexistent-program", "test.json")


def test_artifact_exists(temp_artifacts_dir):
    """Test artifact existence check."""
    write_artifact("test-program", "test.json", {"test": "data"})

    assert artifact_exists("test-program", "test.json")
    assert not artifact_exists("test-program", "nonexistent.json")


def test_list_artifacts(temp_artifacts_dir):
    """Test listing artifacts."""
    write_artifact("test-program", "test1.json", {"data": 1})
    write_artifact("test-program", "test2.md", "# Content")
    write_artifact("test-program", "test3.json", {"data": 2})

    artifacts = list_artifacts("test-program")
    assert len(artifacts) == 3
    assert "test1.json" in artifacts
    assert "test2.md" in artifacts
    assert "test3.json" in artifacts


def test_list_artifacts_empty(temp_artifacts_dir):
    """Test listing artifacts for non-existent program."""
    artifacts = list_artifacts("nonexistent-program")
    assert artifacts == []


def test_write_invalid_artifact_type(temp_artifacts_dir):
    """Test writing artifact with invalid extension."""
    with pytest.raises(ValueError, match="Unknown artifact type"):
        write_artifact("test-program", "test.txt", "content")


def test_load_invalid_artifact_type(temp_artifacts_dir):
    """Test loading artifact with invalid extension."""
    # Create a file with invalid extension
    path = get_artifact_path("test-program", "test.txt")
    path.write_text("content")

    with pytest.raises(ValueError, match="Unknown artifact type"):
        load_artifact("test-program", "test.txt")
