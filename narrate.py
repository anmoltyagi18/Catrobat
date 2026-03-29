#!/usr/bin/env python3
"""
narrate.py — Marine Ecosystem Narration Script
GSoC 2026 Entry Task | Catrobat | Gemini-Powered Ecosystem Narration

Usage:
    python narrate.py                          # Uses data/sample_events.json
    python narrate.py --input data/sample_events.csv
    python narrate.py --input data/sample_events.json --output outputs/result.txt
    python narrate.py --show-prompt            # Prints the prompt before calling Gemini
    python narrate.py --mock                   # Force mock mode (no API key needed)

Environment:
    GEMINI_API_KEY      — Your Google Gemini API key
    OPENROUTER_API_KEY  — Your OpenRouter API key
    OPENROUTER_MODEL    — The model to use on OpenRouter
"""

import argparse
import logging
import os
import sys
from pathlib import Path

from narrator.data_loader import DataLoader
from narrator.prompt_builder import PromptBuilder
from narrator.ai_client import AIClient
from narrator.formatter import OutputFormatter

def load_env(env_path: str = ".env"):
    """
    Load environment variables from a .env file manually.
    Avoids external dependencies like python-dotenv.
    """
    path = Path(env_path)
    if not path.exists():
        return

    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

def setup_logging(verbose: bool):
    """Configure logging level and format."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(levelname)s] %(message)s"
    )

def main():
    parser = argparse.ArgumentParser(
        description="Generate AI-powered narratives from ecosystem simulation data."
    )
    parser.add_argument(
        "--input", "-i", 
        default="data/sample_events.json",
        help="Path to JSON or CSV event file (default: data/sample_events.json)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Path to write narration text (optional)"
    )
    parser.add_argument(
        "--show-prompt",
        action="store_true",
        help="Print the full AI prompt before calling the API"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Force mock mode, skip API call"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable DEBUG logging"
    )

    args = parser.parse_args()
    setup_logging(args.verbose)
    load_env()

    try:
        # 1. Load data
        loader = DataLoader()
        events = loader.load(args.input)
        summary = loader.summarize(events)

        # 2. Build prompt
        builder = PromptBuilder()
        prompt = builder.build(events, summary)

        if args.show_prompt:
            print("\n=== GENERATED PROMPT ===")
            print(prompt)
            print("========================\n")

        # 3. Call AI
        client = AIClient(force_mock=args.mock)
        narration = client.generate(prompt)

        # 4. Format and display
        formatter = OutputFormatter()
        output = formatter.format(narration, client.mode, summary)

        # Print to stdout
        print(output)

        # 5. Write to file if requested
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            logging.info(f"Output written to: {args.output}")

        logging.info(f"Done. Mode: {client.mode} | Events: {len(events)}")

    except FileNotFoundError as e:
        print(f"[ERROR] {str(e)}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"[ERROR] API Failure: {str(e)}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        if args.verbose:
            logging.exception("An unexpected error occurred:")
        else:
            print(f"[ERROR] {str(e)}", file=sys.stderr)
        sys.exit(3)

if __name__ == "__main__":
    main()
