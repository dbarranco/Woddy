"""Step 3: Weekly Planner - Convert week theme to session objectives."""

import os
from anthropic import Anthropic
from pipeline.models import KnowledgeBase
from pipeline.utils import write_artifact, load_artifact
from pipeline.prompts import planner_prompt


def run_planner(
    program_name: str,
    week_number: int,
    macroplan: str = None,
    kb: KnowledgeBase = None,
    model: str = "claude-3-5-haiku-20241022"
) -> str:
    """Generate weekly objectives from macroplan."""

    if macroplan is None:
        macroplan = load_artifact(program_name, "macro-plan.md")

    if kb is None:
        kb = load_artifact(program_name, "knowledge-base.json")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    client = Anthropic(api_key=api_key)

    # Extract this week's section from macroplan
    week_section = f"[Week {week_number}]"
    lines = macroplan.split("\n")
    week_content = ""
    capture = False
    for line in lines:
        if f"Week {week_number}" in line:
            capture = True
        elif capture and line.startswith("## Week"):
            break
        if capture:
            week_content += line + "\n"

    prompt = planner_prompt(week_content or macroplan, week_number, kb)

    print(f"🔄 Planning Week {week_number} objectives...")
    raw_response = ""

    with client.messages.stream(
        model=model,
        max_tokens=3000,
        system="You are a program designer. Convert week themes into clear session objectives.",
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            raw_response += text
            print(".", end="", flush=True)

    print()
    write_artifact(program_name, f"week-{week_number}-objective.md", raw_response)
    print(f"✅ Generated Week {week_number} objectives")

    return raw_response
