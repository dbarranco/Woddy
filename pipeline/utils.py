"""Utility functions for pipeline steps."""

import json
from pathlib import Path
from typing import Any, Dict

ARTIFACTS_DIR = Path(__file__).parent.parent / "artifacts"


def get_artifact_path(program_name: str, filename: str) -> Path:
    """Get full path to artifact file."""
    artifact_dir = ARTIFACTS_DIR / program_name
    artifact_dir.mkdir(parents=True, exist_ok=True)
    return artifact_dir / filename


def write_artifact(program_name: str, filename: str, data: Any) -> None:
    """Write artifact as JSON or Markdown."""
    path = get_artifact_path(program_name, filename)
    if filename.endswith(".json"):
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    elif filename.endswith(".md"):
        with open(path, "w") as f:
            f.write(data)
    else:
        raise ValueError(f"Unknown artifact type: {filename}")
    print(f"✅ Wrote {path}")


def load_artifact(program_name: str, filename: str) -> Any:
    """Load artifact from disk."""
    path = get_artifact_path(program_name, filename)
    if not path.exists():
        raise FileNotFoundError(f"Artifact not found: {path}")

    if filename.endswith(".json"):
        with open(path) as f:
            return json.load(f)
    elif filename.endswith(".md"):
        with open(path) as f:
            return f.read()
    raise ValueError(f"Unknown artifact type: {filename}")


def list_artifacts(program_name: str) -> list:
    """List all artifacts for a program."""
    path = ARTIFACTS_DIR / program_name
    if not path.exists():
        return []
    return [f.name for f in path.glob("*")]


def artifact_exists(program_name: str, filename: str) -> bool:
    """Check if an artifact exists."""
    path = get_artifact_path(program_name, filename)
    return path.exists()
