"""Step 5: Summarizer - Extract metrics from week's sessions (pure Python)."""

import json
from collections import defaultdict
from pipeline.models import WeekSummary
from pipeline.utils import load_artifact, write_artifact


def run_summarizer(program_name: str, week_number: int) -> WeekSummary:
    """Extract metrics from all 5 daily sessions."""

    # Load all 5 session JSONs
    sessions = []
    for day in range(1, 6):
        try:
            session = load_artifact(program_name, f"week-{week_number}-day-{day}.json")
            sessions.append(session)
        except FileNotFoundError:
            print(f"⚠️  W{week_number}D{day} not found, skipping")

    if not sessions:
        print(f"❌ No sessions found for week {week_number}")
        return None

    # Extract metrics
    total_reps = 0
    total_tonnage = 0
    movement_frequency: defaultdict[str, int] = defaultdict(int)
    push_count = 0
    pull_count = 0
    intensity_distribution = {"heavy_70_85": 0, "moderate_60_70": 0, "light_50_60": 0}
    energy_systems = {"cns_intensive": 0, "glycolytic": 0, "aerobic": 0}
    pattern_concerns = []

    push_movements = {"press", "bench", "dumbbell press", "push", "thruster", "jerk"}
    pull_movements = {"pull", "row", "deadlift", "clean", "snatch"}

    for session in sessions:
        if isinstance(session, dict) and "blocks" in session:
            for block in session.get("blocks", []):
                for item in block.get("content", []):
                    if isinstance(item, dict):
                        movement_name = item.get("movement", "").lower()
                        reps = item.get("reps", 0)
                        weight = item.get("weight_lb", 0)

                        total_reps += reps
                        total_tonnage += weight * reps
                        movement_frequency[movement_name] += 1

                        # Classify push/pull
                        if any(p in movement_name for p in push_movements):
                            push_count += 1
                        elif any(p in movement_name for p in pull_movements):
                            pull_count += 1

    # Check for pattern concerns
    for movement, count in movement_frequency.items():
        if count > 2:
            pattern_concerns.append(f"{movement} appears {count} times")

    # Calculate push:pull ratio
    push_pull_ratio = push_count / max(pull_count, 1)

    # Create summary
    summary: WeekSummary = {
        "week": week_number,
        "total_volume": {
            "reps": total_reps,
            "tonnage_lb": total_tonnage,
            "sessions": len(sessions)
        },
        "push_pull_ratio": round(push_pull_ratio, 2),
        "movement_frequency": dict(movement_frequency),
        "intensity_distribution": intensity_distribution,
        "energy_systems": energy_systems,
        "pattern_concerns": pattern_concerns
    }

    write_artifact(program_name, f"week-{week_number}-summary.json", summary)
    print(f"✅ Summarized Week {week_number}: {total_reps} reps, {total_tonnage} tons")

    return summary
