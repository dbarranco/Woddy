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
from pipeline.logging_utils import PipelineLogger


def run_pipeline(
    program_name: str,
    weeks: int,
    model: str = "claude-3-5-haiku-20241022",
    verbose: bool = True,
    force: bool = False
) -> None:
    """Execute the full 7-step pipeline with caching and cost tracking."""

    logger = PipelineLogger(program_name, verbose=verbose)

    print(f"\n🚀 Starting pipeline for '{program_name}' ({weeks} weeks)")
    print(f"📊 Model: {model} | 🔄 Force: {force}")
    print("=" * 60)

    # Step 1: Knowledge Curator (one-time, can be cached)
    print("\n📚 Step 1: Knowledge Curator")
    if not force and logger.should_skip_step("step_1_curator", program_name):
        print("   📦 Using cached knowledge base")
        kb = None  # Will be loaded on-demand
        logger.log_step("step_1_curator", cached=True)
    else:
        print("   Extracting knowledge base from bibliography...")
        kb = run_curator(program_name=program_name, model=model)
        logger.log_step("step_1_curator", input_tokens=15000, output_tokens=3000)

    # Step 2: Program Strategist (can be cached)
    print("\n📋 Step 2: Program Strategist")
    if not force and logger.should_skip_step("step_2_strategist", program_name):
        print("   📦 Using cached macroplan")
        logger.log_step("step_2_strategist", cached=True)
    else:
        print("   Designing week-by-week macroplan...")
        macroplan = run_strategist(program_name, weeks, kb, model)
        logger.log_step("step_2_strategist", input_tokens=8000, output_tokens=2000)

    # Steps 3-6: Process each week
    for week in range(1, weeks + 1):
        print(f"\n📅 Week {week} Processing")

        # Step 3: Weekly Planner (can be cached)
        if not force and logger.should_skip_step("step_3_planner", program_name):
            print(f"  ✅ Step 3: Using cached week {week} objectives")
            logger.log_step(f"step_3_planner_w{week}", cached=True)
        else:
            print(f"  ✅ Step 3: Planning week {week} sessions...")
            objectives = run_planner(program_name, week, None, kb, model)
            logger.log_step(f"step_3_planner_w{week}", input_tokens=6000, output_tokens=1500)

        # Step 4: Session Composer (5 sessions per week)
        print(f"  ✅ Step 4: Composing 5 sessions...")
        sessions_generated = 0
        for day in range(1, 6):
            session = run_composer(program_name, week, day, None, kb, model=model)
            sessions_generated += 1
            # Estimate tokens per session
            logger.log_step(f"step_4_composer_w{week}d{day}", input_tokens=7000, output_tokens=4000)

        # Step 5: Summarizer (pure Python, no API cost)
        print(f"  ✅ Step 5: Summarizing week metrics...")
        summary = run_summarizer(program_name, week)
        logger.log_step(f"step_5_summarizer_w{week}", cached=True)  # No API call

        # Step 6: Validator (pure logic-based)
        print(f"  ✅ Step 6: Validating week constraints...")
        validation = run_validator(program_name, week, kb, model)
        if validation["issues"]:
            print(f"     ⚠️  Found {len(validation['issues'])} issues")
        logger.log_step(f"step_6_validator_w{week}", cached=True)  # No API call

    # Step 7: Assemble (pure Python)
    print("\n📦 Step 7: Assembling final program...")
    program = run_assemble(program_name, weeks)
    logger.log_step("step_7_assemble", cached=True)  # No API call

    # Print summary
    metrics = logger.summary()
    print(f"✅ Pipeline complete! Generated {len(program['sessions'])} sessions")
    print(f"📂 Output: output/{program_name}-{weeks}w.json")
    print(f"💾 Artifacts: artifacts/{program_name}/")
    return metrics


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Woddy Pipeline: 7-step training program generator")
    parser.add_argument("--name", required=True, help="Program name (e.g., 'back-in-shape')")
    parser.add_argument("--weeks", type=int, required=True, help="Number of weeks (2-4)")
    parser.add_argument("--model", default="claude-3-5-haiku-20241022", help="Claude model to use")
    parser.add_argument("--force", action="store_true", help="Force re-run of all steps (ignore cache)")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output")

    args = parser.parse_args()

    if not (2 <= args.weeks <= 4):
        print("❌ Error: weeks must be between 2 and 4")
        sys.exit(1)

    try:
        metrics = run_pipeline(
            args.name,
            args.weeks,
            args.model,
            verbose=not args.quiet,
            force=args.force
        )
        sys.exit(0)
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
