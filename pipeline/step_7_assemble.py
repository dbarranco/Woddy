"""Step 7: Assemble - Merge all validated weeks into final program."""

import json
from pathlib import Path
from pipeline.utils import load_artifact


def run_assemble(program_name: str, weeks: int) -> dict:
    """Merge all weeks into final program JSON."""

    # Collect all session JSONs
    sessions = []
    for week in range(1, weeks + 1):
        for day in range(1, 6):
            try:
                session = load_artifact(program_name, f"week-{week}-day-{day}.json")
                sessions.append(session)
            except:
                pass

    # Build final program
    program = {
        "metadata": {
            "name": program_name,
            "weeks": weeks,
            "total_sessions": len(sessions),
            "generated_at": "2026-06-29"
        },
        "sessions": sessions
    }

    # Write to output
    output_file = Path(__file__).parent.parent / "output" / f"{program_name}-{weeks}w.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(program, f, indent=2)

    print(f"✅ Assembled {len(sessions)} sessions into {output_file.name}")

    # Also save markdown preview
    preview_file = output_file.with_suffix(".md")
    with open(preview_file, "w") as f:
        f.write(f"# {program_name.title()} - {weeks}-Week Program\n\n")
        f.write(f"**Total Sessions**: {len(sessions)}\n\n")
        for i, session in enumerate(sessions, 1):
            title = session.get("title", f"Session {i}")
            week = session.get("week", "?")
            day = session.get("day", "?")
            f.write(f"## Week {week} Day {day}: {title}\n")
            f.write(f"- Focus: {session.get('focus', 'N/A')}\n")
            f.write(f"- Equipment: {', '.join(session.get('equipment', []))}\n\n")

    print(f"✅ Generated preview: {preview_file.name}")

    return program
