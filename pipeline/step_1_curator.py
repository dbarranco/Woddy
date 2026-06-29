"""Step 1: Knowledge Curator - Extract structured rules from bibliography."""

import json
import os
from pathlib import Path
from anthropic import Anthropic
from pipeline.models import KnowledgeBase
from pipeline.utils import write_artifact
from pipeline.prompts import curator_prompt


def run_curator(program_name: str = "shared", model: str = "claude-3-5-haiku-20241022") -> KnowledgeBase:
    """Extract knowledge base from bibliography files."""

    # Read all knowledge base files
    kb_dir = Path(__file__).parent.parent / "knowledge-base"
    kb_files = sorted(kb_dir.glob("*.md"))

    if not kb_files:
        raise FileNotFoundError(f"No knowledge base files found in {kb_dir}")

    # Concatenate all knowledge base content
    kb_text = "\n\n".join(f"## {f.stem}\n{f.read_text()}" for f in kb_files)

    # Initialize Anthropic client
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    client = Anthropic(api_key=api_key)

    # Get curator prompt
    prompt = curator_prompt(kb_text)

    # Call Claude API with streaming for large knowledge base
    print(f"🔄 Extracting knowledge base to structured JSON...")
    raw_response = ""

    with client.messages.stream(
        model=model,
        max_tokens=4000,
        system="You are a sports science knowledge curator. Extract rules, principles, and loading schemes from the provided knowledge base and output only valid JSON.",
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            raw_response += text
            print(".", end="", flush=True)

    print()  # newline

    # Parse JSON response
    try:
        # Try to extract JSON from response (in case there's surrounding text)
        json_start = raw_response.find("{")
        json_end = raw_response.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            json_str = raw_response[json_start:json_end]
            kb_data = json.loads(json_str)
        else:
            kb_data = json.loads(raw_response)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON response: {e}")
        print(f"Response:\n{raw_response[:500]}")
        raise

    # Validate structure
    kb: KnowledgeBase = {
        "meta": kb_data.get("meta", {"last_updated": "2026-06-29", "source": "knowledge-base"}),
        "rules": kb_data.get("rules", []),
        "principles": kb_data.get("principles", []),
        "loading_schemes": kb_data.get("loading_schemes", {})
    }

    # Write artifact
    write_artifact(program_name, "knowledge-base.json", kb)
    print(f"✅ Extracted {len(kb['rules'])} rules and {len(kb['principles'])} principles")

    return kb


if __name__ == "__main__":
    kb = run_curator()
    print(f"\n📊 Knowledge Base Summary:")
    print(f"  Rules: {len(kb['rules'])}")
    print(f"  Principles: {len(kb['principles'])}")
    print(f"  Loading schemes: {list(kb['loading_schemes'].keys())}")
