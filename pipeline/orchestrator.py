"""Pipeline Orchestrator - Main entry point for 7-step generation pipeline."""

import argparse
import sys
from pathlib import Path

# Import all pipeline steps
from pipeline.step_1_curator import run_curator
from pipeline.step_2_strategist import run_strategist
from pipeline.step_3_planner import run_planner
from pipeline.step_4_composer import run_composer
from pipeline.step_5_summarizer import run_summarizer
from pipeline.step_6_validator import run_validator
from pipeline.step_7_assemble import run_assemble


def run_pipeline(program_name: str, weeks: int, model: str = "claude-3-5-haiku-20241022") -> None:
    """Execute the full 7-step pipeline."""

    print(f"\n🚀 Starting pipeline for '{program_name}' ({weeks} weeks)")
    print("=" * 60)

    # Step 1: Knowledge Curator (one-time)
    print("\n📚 Step 1: Knowledge Curator (extracting knowledge base)...")
    kb = run_curator(program_name=program_name, model=model)

    # Step 2: Program Strategist
    print("\n📋 Step 2: Program Strategist (designing macroplan)...")
    macroplan = run_strategist(program_name, weeks, kb, model)

    # Steps 3-6: Process each week
    for week in range(1, weeks + 1):
        print(f"\n📅 Week {week} Processing...")

        # Step 3: Weekly Planner
        print(f"  Step 3: Planning Week {week}...")
        objectives = run_planner(program_name, week, macroplan, kb, model)

        # Step 4: Session Composer (5 sessions per week)
        print(f"  Step 4: Composing 5 sessions...")
        for day in range(1, 6):
            run_composer(program_name, week, day, objectives, kb, model=model)

        # Step 5: Summarizer (pure Python)
        print(f"  Step 5: Summarizing week metrics...")
        summary = run_summarizer(program_name, week)

        # Step 6: Validator with retry logic
        print(f"  Step 6: Validating week...")
        validation = run_validator(program_name, week, kb, model)

        if not validation["valid"] and validation["retry_count"] < validation["max_retries"]:
            print(f"⚠️  Week {week} validation failed. Regenerating sessions...")
            # TODO: Implement retry logic (regenerate Step 4)

    # Step 7: Assemble
    print("\n📦 Step 7: Assembling final program...")
    program = run_assemble(program_name, weeks)

    print("\n" + "=" * 60)
    print(f"✅ Pipeline complete! Generated {len(program['sessions'])} sessions")
    print(f"📂 Output: output/{program_name}-{weeks}w.json")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Woddy Pipeline: 7-step training program generator")
    parser.add_argument("--name", required=True, help="Program name (e.g., 'back-in-shape')")
    parser.add_argument("--weeks", type=int, required=True, help="Number of weeks (2-4)")
    parser.add_argument("--model", default="claude-3-5-haiku-20241022", help="Claude model to use")

    args = parser.parse_args()

    if not (2 <= args.weeks <= 4):
        print("❌ Error: weeks must be between 2 and 4")
        sys.exit(1)

    try:
        run_pipeline(args.name, args.weeks, args.model)
    except KeyboardInterrupt:
        print("\n\n⛔ Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
