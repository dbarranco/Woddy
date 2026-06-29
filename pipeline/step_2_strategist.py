"""Step 2: Program Strategist - Design overall training arc."""

import os
import json
from anthropic import Anthropic
from pipeline.models import KnowledgeBase, MacroPlan
from pipeline.utils import write_artifact, load_artifact
from pipeline.prompts import strategist_prompt


def run_strategist(
    program_name: str,
    weeks: int,
    kb: KnowledgeBase = None,
    model: str = "claude-3-5-haiku-20241022"
) -> str:
    """Generate macroplan from knowledge base."""

    if kb is None:
        kb = load_artifact(program_name, "knowledge-base.json")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    client = Anthropic(api_key=api_key)

    prompt = strategist_prompt(kb, program_name, weeks)

    print(f"🔄 Generating {weeks}-week macroplan...")
    raw_response = ""

    with client.messages.stream(
        model=model,
        max_tokens=3000,
        system="You are a periodization expert. Design detailed week-by-week training arcs with progression principles.",
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            raw_response += text
            print(".", end="", flush=True)

    print()
    write_artifact(program_name, "macro-plan.md", raw_response)
    print(f"✅ Generated {weeks}-week macroplan")

    return raw_response


if __name__ == "__main__":
    # Test: Load KB, generate macroplan for 2-week program
    from pipeline.step_1_curator import run_curator

    kb = run_curator()
    macroplan = run_strategist("test-program", weeks=2, kb=kb)
    print(f"\n📋 Macroplan Preview:\n{macroplan[:300]}...")
