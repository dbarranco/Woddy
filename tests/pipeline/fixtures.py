"""Shared test fixtures for pipeline tests."""

import pytest
from typing import Dict, Any
from pipeline.models import KnowledgeBase, Rule, Principle


@pytest.fixture
def sample_knowledge_base() -> KnowledgeBase:
    """Minimal knowledge base for testing."""
    return {
        "meta": {"last_updated": "2026-06-29", "source": "knowledge-base/*.md"},
        "rules": [
            {
                "id": "volume-progression",
                "rule": "No volume increase >15% week-over-week",
                "source": "Bompa & Haff",
                "category": "safety",
                "priority": "critical"
            },
            {
                "id": "consecutive-oly",
                "rule": "No Olympic lifts on consecutive days",
                "source": "CrossFit Level 2 Training Guide",
                "category": "cns-fatigue",
                "priority": "critical"
            },
            {
                "id": "push-pull-ratio",
                "rule": "Push:pull ratio ≥ 1:1 per week",
                "source": "NSCA Essentials 4th ed",
                "category": "movement-balance",
                "priority": "high"
            }
        ],
        "principles": [
            {
                "id": "energy-systems",
                "name": "Energy System Interaction",
                "summary": "Aerobic base first, then power/strength, then glycolytic work",
                "source": "Gastin 2001"
            },
            {
                "id": "periodization",
                "name": "Linear Periodization (4-week macro)",
                "summary": "Week 1: General prep. Week 2-3: Strength/hypertrophy. Week 4: Deload",
                "source": "Bompa & Haff"
            }
        ],
        "loading_schemes": {
            "strength": {"range": [70, 85], "unit": "%1RM", "reps": "1-5"},
            "hypertrophy": {"range": [65, 75], "unit": "%1RM", "reps": "6-12"},
            "power": {"range": [75, 90], "unit": "%1RM", "reps": "1-5"},
            "endurance": {"range": [40, 60], "unit": "%1RM", "reps": "15+"}
        }
    }


@pytest.fixture
def sample_program_config() -> Dict[str, Any]:
    """Program generation config."""
    return {
        "name": "back-in-shape",
        "weeks": 2,
        "goal": "General fitness"
    }


@pytest.fixture
def sample_rule() -> Rule:
    """Single rule for testing."""
    return {
        "id": "test-rule",
        "rule": "Test rule text",
        "source": "Test Source",
        "category": "test",
        "priority": "high"
    }


@pytest.fixture
def sample_principle() -> Principle:
    """Single principle for testing."""
    return {
        "id": "test-principle",
        "name": "Test Principle Name",
        "summary": "Test principle summary",
        "source": "Test Source"
    }
