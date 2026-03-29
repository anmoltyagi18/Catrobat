import os
import sys
# Ensure we can import narrator
sys.path.append(os.getcwd())

from narrator.prompt_builder import PromptBuilder

builder = PromptBuilder()
prompt = builder.build([], {})
print(f"Length: {len(prompt)}")
print(f"MarineNarrator: {'MarineNarrator' in prompt}")
print(f"2 to 4 sentences: {'2 to 4 sentences' in prompt}")
print(f"2-4 sentence: {'2-4 sentence' in prompt}")
