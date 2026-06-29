"""Logging and observability utilities."""

import time
from datetime import datetime
from typing import Optional
from pathlib import Path


class PipelineLogger:
    """Track execution metrics: tokens, cost, time."""

    def __init__(self, program_name: str, verbose: bool = True):
        self.program_name = program_name
        self.verbose = verbose
        self.steps = {}
        self.start_time = time.time()

        # Haiku pricing: $0.80 per 1M input, $0.40 per 1M output
        self.input_cost_per_mtok = 0.80 / 1_000_000
        self.output_cost_per_mtok = 0.40 / 1_000_000

    def log_step(
        self,
        step_name: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cached: bool = False
    ):
        """Log a step's token usage and cost."""
        total_tokens = input_tokens + output_tokens
        step_cost = (input_tokens * self.input_cost_per_mtok) + (output_tokens * self.output_cost_per_mtok)

        self.steps[step_name] = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "cost": step_cost,
            "cached": cached,
            "timestamp": datetime.now().isoformat()
        }

        if self.verbose:
            status = "📦 CACHED" if cached else "✅"
            print(f"{status} {step_name}")
            if not cached and total_tokens > 0:
                print(f"   Tokens: {input_tokens:,} in + {output_tokens:,} out = {total_tokens:,} total")
                print(f"   Cost: ${step_cost:.6f}")

    def summary(self):
        """Print pipeline summary."""
        elapsed = time.time() - self.start_time
        total_tokens = sum(s["total_tokens"] for s in self.steps.values() if not s["cached"])
        total_cost = sum(s["cost"] for s in self.steps.values() if not s["cached"])

        print("\n" + "=" * 60)
        print(f"📊 Pipeline Summary: {self.program_name}")
        print("=" * 60)

        for step_name, data in self.steps.items():
            if data["cached"]:
                print(f"  {step_name:<30} CACHED")
            else:
                print(f"  {step_name:<30} {data['total_tokens']:>7,} tokens | ${data['cost']:>8.6f}")

        print("-" * 60)
        print(f"  {'TOTAL':<30} {total_tokens:>7,} tokens | ${total_cost:>8.6f}")
        print(f"  {'Time':<30} {elapsed:>7.1f}s")
        print("=" * 60 + "\n")

        return {
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "elapsed_seconds": elapsed,
            "steps": self.steps
        }

    def should_skip_step(self, step_name: str, program_name: str) -> bool:
        """Check if step output already exists (caching logic)."""
        artifact_dir = Path(__file__).parent.parent / "artifacts" / program_name

        # Define which artifacts indicate step completion
        completion_markers = {
            "step_1_curator": "knowledge-base.json",
            "step_2_strategist": "macro-plan.md",
            "step_3_planner": lambda w: f"week-{w}-objective.md",
            "step_4_composer": lambda w: f"week-{w}-day-1.json",
            "step_5_summarizer": lambda w: f"week-{w}-summary.json",
            "step_6_validator": lambda w: f"week-{w}-validation.json",
        }

        if step_name not in completion_markers:
            return False

        marker = completion_markers[step_name]
        if callable(marker):
            # For week-based steps, check if at least week 1 exists
            return (artifact_dir / marker(1)).exists()
        else:
            return (artifact_dir / marker).exists()
