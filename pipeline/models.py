"""Shared data structures for pipeline steps."""

from typing import TypedDict, List, Dict, Any, Optional


class Rule(TypedDict):
    """Single constraint rule from knowledge base."""
    id: str
    rule: str
    source: str
    category: str
    priority: str  # "critical" or "high"


class Principle(TypedDict):
    """Domain knowledge principle."""
    id: str
    name: str
    summary: str
    source: str


class LoadingScheme(TypedDict):
    """Loading percentage ranges for training zones."""
    range: List[int]  # [min, max]
    unit: str        # "%1RM"
    reps: Optional[str]


class KnowledgeBase(TypedDict):
    """Structured knowledge extracted from bibliography."""
    meta: Dict[str, str]
    rules: List[Rule]
    principles: List[Principle]
    loading_schemes: Dict[str, LoadingScheme]


class MacroPlan(TypedDict):
    """High-level program structure."""
    program_name: str
    weeks: int
    weeks_data: Dict[str, Any]  # week_1, week_2, etc.


class WeeklyObjective(TypedDict):
    """Session-level objectives for one week."""
    week: int
    sessions: Dict[str, Any]  # w1d1, w1d2, etc.


class SessionData(TypedDict):
    """Full JSON session (matches current output schema)."""
    id: str
    week: int
    day: int
    is_rest_day: bool
    title: str
    # Note: additional fields from current schema will be added at runtime


class WeekSummary(TypedDict):
    """Metrics extracted from a week's sessions."""
    week: int
    total_volume: Dict[str, int]
    push_pull_ratio: float
    movement_frequency: Dict[str, int]
    intensity_distribution: Dict[str, int]
    energy_systems: Dict[str, int]
    pattern_concerns: List[str]


class ValidationIssue(TypedDict):
    """Single validation finding."""
    rule_id: str
    severity: str  # "critical", "high", "warning"
    message: str
    action: str    # "regenerate", "monitor", "pass"


class ValidationResult(TypedDict):
    """Validator output."""
    week: int
    validation_timestamp: str
    valid: bool
    issues: List[ValidationIssue]
    retry_count: int
    max_retries: int
