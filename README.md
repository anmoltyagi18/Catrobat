# 🌊 Gemini-Powered Ecosystem Narration

[![CI — Ecosystem Narration Tests](https://github.com/YOUR_USERNAME/gemini-ecosystem-narration/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/gemini-ecosystem-narration/actions)

## Overview
This project is an AI-powered narration and explainability layer for marine ecosystem simulations. It leverages the **Google Gemini API** (and support for **OpenRouter/Gemma 3**) to translate raw JSON/CSV simulation event logs into engaging, scientifically accurate 2–4 sentence ecological summaries. 

This project corresponds to the **Google Summer of Code 2026** project idea: *"Gemini-Powered Ecosystem Narration"* for the **Catrobat** organization.

## Entry Task Deliverables
- [x] Script (`narrate.py`)
- [x] Sample dataset (`data/sample_events.json`, `data/sample_events.csv`)
- [x] README (this file)
- [x] Sample output (`outputs/sample_output.txt`)
- [x] Unit tests (37 tests, all passing)
- [x] CI pipeline (GitHub Actions)

## Quick Start (No API key required)
The script includes a robust **Mock Mode** for evaluation without an API key.

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/gemini-ecosystem-narration.git
cd gemini-ecosystem-narration

# Install dependencies (Standard Library + Gemini/OpenAI SDKs)
pip install -r requirements.txt

# Run the simulation narration in Mock Mode
python narrate.py --mock
```

## Full Setup (With API Key)
The project supports both native **Google Gemini** and **OpenRouter**.

```bash
# 1. Prepare environment
cp .env.example .env

# 2. Edit .env and paste your GEMINI_API_KEY or OPENROUTER_API_KEY
# If using OpenRouter, specify OPENROUTER_MODEL=google/gemma-3-4b-it:free (already defaulted)

# 3. Run live narration
python narrate.py
```

## Usage — All CLI Options
| Flag | Description | Default |
|------|-------------|---------|
| `--input`, `-i` | Path to JSON or CSV event file | `data/sample_events.json` |
| `--output`, `-o` | Write narration to this file (optional) | None |
| `--show-prompt` | Print the full Gemini prompt before calling API | False |
| `--mock` | Force mock mode, skip API call | False |
| `--verbose`, `-v` | Enable DEBUG logging | False |

## Sample Output
```text
╔══════════════════════════════════════════════════════════════════════════════╗
║  MARINE ECOSYSTEM NARRATION  [MOCK]                                          ║
║  Events analyzed: 12 | High severity: 1                                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  A spawning surge of clownfish in Reef Zone A signals healthy reproductive   ║
║  activity, though the concurrent moderate coral bleaching in the same zone   ║
║  raises urgent concern for long-term habitat viability. A solitary shark     ║
║  patrolling the deep zone is likely drawn by the increased prey density      ║
║  near the reef, while a high-density plankton bloom at the surface suggests  ║
║  elevated nutrient upwelling — a phenomenon that may cascade positively      ║
║  through the food web if water temperatures remain stable.                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## The Prompt Design
The core of this project is a carefully engineered prompt located in `narrator/prompt_builder.py`.

- **Structured System Context**: `SYSTEM_CONTEXT` defines the AI's persona as "MarineNarrator" and enforces 7 strict rules.
- **Controlled Temperature (0.4)**: Chosen to balance scientific accuracy with creative prose, ensuring summaries are factual yet engaging.
- **Spatial Grouping**: Simulation events are grouped by `zone` before being fed to the model, helping the LLM identify localized spatial patterns and causal relationships.
- **Narrative Anchors**: The `Summary Statistics` block provides a ground-truth "anchor" (total counts, organisms involved), preventing the model from hallucinating organisms or events not present in the data.
- **Present Tense Enforcement**: Specified in the rules to make the simulation feel "alive" and interactive, as if a scientist is narrating a live feed.

## Running Tests
Unit tests use `pytest` and mock all external API calls.
```bash
# Install testing dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest tests/ -v

# Check coverage report
pytest tests/ --cov=narrator --cov-report=term-missing
```
*Expected: 37 passed.*

## Project Structure
```text
gemini-ecosystem-narration/
├── narrate.py                ← Main narration script
├── narrator/                 ← Core logic package
│   ├── data_loader.py        ← JSON/CSV validation
│   ├── prompt_builder.py     ← Gemini prompt engineering
│   ├── ai_client.py          ← API Client (Gemini & OpenRouter)
│   └── formatter.py          ← Box-style CLI formatting
├── data/                     ← Simulation data samples
├── outputs/                  ← Pre-generated results
├── tests/                    ← Comprehensive unit tests
├── .github/workflows/ci.yml  ← Automated CI tests
├── requirements.txt          ← Production requirements
└── README.md                 ← This documentation
```

## Architecture Diagram
```text
┌─────────────────────────────────────────────────────────┐
│                      narrate.py                         │
│  (CLI entry point — argparse, logging, .env loading)    │
└──────────┬───────────────────────────────────┬──────────┘
           │                                   │
           ▼                                   ▼
  ┌────────────────┐                 ┌──────────────────┐
  │  DataLoader    │                 │  OutputFormatter │
  │  .load()       │                 │  .format()       │
  │  .summarize()  │                 │  .clean()        │
  └───────┬────────┘                 └────────┬─────────┘
          │                                   │
          ▼                                   │
  ┌────────────────┐                          │
  │ PromptBuilder  │                          │
  │  .build()      │                          │
  └───────┬────────┘                          │
          │                                   │
          ▼                                   │
  ┌────────────────┐                          │
  │    AIClient    │──────────────────────────┘
  │  .generate()   │
  │  ↳ Live / Mock │
  └────────────────┘
```

## GSoC Project Idea Reference
Link: [Catrobat GSoC 2026 Ideas](https://developer.catrobat.org/pages/development/google-summer-of-code/2026/)

## License
MIT License - Copyright (c) 2026 YOUR_NAME

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

## Author
[YOUR_NAME] - [GitHub Profile Link]
GSoC 2026 applicant — Catrobat
