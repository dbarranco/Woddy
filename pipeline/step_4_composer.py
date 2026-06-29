"""Step 4: Session Composer - Generate full 60-minute sessions as JSON."""

import os
import json
from anthropic import Anthropic
from pipeline.utils import write_artifact, load_artifact
from pipeline.prompts import composer_prompt


def run_composer(
    program_name: str,
    week_number: int,
    day_number: int,
    objectives: str = None,
    kb = None,
    movement_library = None,
    prev_session = None,
    model: str = "claude-3-5-haiku-20241022"
) -> dict:
    """Generate a full session as JSON."""

    if objectives is None:
        objectives = load_artifact(program_name, f"week-{week_number}-objective.md")

    if kb is None:
        kb = load_artifact(program_name, "knowledge-base.json")

    if movement_library is None:
        try:
            movement_library = load_artifact(program_name, "movement-library.json")
        except:
            movement_library = {}

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    client = Anthropic(api_key=api_key)

    prompt = composer_prompt(objectives, week_number, day_number, kb, movement_library, prev_session)

    print(f"🔄 Composing W{week_number}D{day_number} session...")
    raw_response = ""

    with client.messages.stream(
        model=model,
        max_tokens=4000,
        system="You are a CrossFit programming expert. Output only valid JSON for a complete 60-minute session.",
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            raw_response += text

    # Parse JSON from response
    try:
        json_start = raw_response.find("{")
        json_end = raw_response.rfind("}") + 1
        json_str = raw_response[json_start:json_end]
        session_data = json.loads(json_str)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"⚠️  Failed to parse session JSON: {e}")
        session_data = {"error": "JSON parsing failed"}

    write_artifact(program_name, f"week-{week_number}-day-{day_number}.json", session_data)
    print(f"✅ Generated W{week_number}D{day_number}")

    return session_data
