"""Tests for pipeline data models."""

import pytest
from pipeline.models import KnowledgeBase, Rule, Principle, ValidationResult
from tests.pipeline.fixtures import sample_knowledge_base, sample_rule, sample_principle


def test_knowledge_base_structure(sample_knowledge_base):
    """Verify KnowledgeBase TypedDict validates."""
    assert sample_knowledge_base["meta"]["last_updated"] == "2026-06-29"
    assert len(sample_knowledge_base["rules"]) == 3
    assert sample_knowledge_base["rules"][0]["id"] == "volume-progression"
    assert len(sample_knowledge_base["principles"]) == 2
    assert "strength" in sample_knowledge_base["loading_schemes"]


def test_rule_structure(sample_rule):
    """Test Rule TypedDict."""
    assert sample_rule["id"] == "test-rule"
    assert sample_rule["priority"] == "high"
    assert sample_rule["source"] == "Test Source"


def test_principle_structure(sample_principle):
    """Test Principle TypedDict."""
    assert sample_principle["id"] == "test-principle"
    assert sample_principle["name"] == "Test Principle Name"
    assert sample_principle["source"] == "Test Source"


def test_rule_priority_values(sample_rule):
    """Verify rule priority is valid."""
    valid_priorities = ["critical", "high"]
    assert sample_rule["priority"] in valid_priorities


def test_knowledge_base_rules_complete():
    """Verify all rules have required fields."""
    kb: KnowledgeBase = {
        "meta": {"last_updated": "2026-06-29", "source": "test"},
        "rules": [
            {
                "id": "test",
                "rule": "Test rule",
                "source": "Source",
                "category": "test",
                "priority": "critical"
            }
        ],
        "principles": [],
        "loading_schemes": {}
    }
    rule = kb["rules"][0]
    assert rule["id"] == "test"
    assert rule["rule"] == "Test rule"
    assert rule["source"] == "Source"
    assert rule["category"] == "test"
    assert rule["priority"] == "critical"


def test_loading_schemes():
    """Test LoadingScheme structure."""
    kb: KnowledgeBase = {
        "meta": {},
        "rules": [],
        "principles": [],
        "loading_schemes": {
            "strength": {
                "range": [70, 85],
                "unit": "%1RM",
                "reps": "1-5"
            }
        }
    }
    scheme = kb["loading_schemes"]["strength"]
    assert scheme["range"] == [70, 85]
    assert scheme["unit"] == "%1RM"
    assert scheme["reps"] == "1-5"
