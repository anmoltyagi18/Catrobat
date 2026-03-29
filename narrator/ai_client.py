import os
import json
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

MOCK_NARRATION = """A spawning surge of clownfish in Reef Zone A signals
healthy reproductive activity, though the concurrent moderate coral
bleaching in the same zone raises urgent concern for long-term habitat
viability. A solitary shark patrolling the deep zone is likely drawn by
the increased prey density near the reef, while a high-density plankton
bloom at the surface suggests elevated nutrient upwelling — a phenomenon
that may cascade positively through the food web if water temperatures
remain stable."""

class AIClient:
    """
    Sends a prompt to an AI provider (Google Gemini or OpenRouter) 
    and returns the generated narration text.

    If no API keys are set, the client automatically falls back to 
    a pre-generated mock narration for demonstration purposes.
    """

    GEMINI_MODEL = "gemini-2.0-flash"
    OPENROUTER_MODEL = "google/gemma-3-4b-it:free"
    MAX_TOKENS = 512
    TEMPERATURE = 0.4

    def __init__(self, force_mock: bool = False):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_model = os.getenv("OPENROUTER_MODEL", self.OPENROUTER_MODEL)
        
        self.is_mock = force_mock or (not self.gemini_key and not self.openrouter_key)
        
        if self.is_mock:
            logger.warning(
                "No API keys set or mock mode forced. Running in MOCK mode. "
                "Output is pre-generated for demonstration purposes."
            )

    def generate(self, prompt: str) -> str:
        """
        Call the AI API with the given prompt and return the narration text.
        Falls back to MOCK_NARRATION if no API key is present.
        """
        try:
            if self.is_mock:
                return self._mock_response()
            
            # Prioritize OpenRouter if key is present
            if self.openrouter_key:
                return self._call_openrouter(prompt)
            
            # Otherwise fallback to Gemini
            return self._call_gemini(prompt)
        except RuntimeError:
            # Already wrapped by _call_gemini or _call_openrouter
            raise
        except Exception as e:
            # Catch raw exceptions that might bubble up (e.g. from mock settings)
            raise RuntimeError(f"API call failed: {str(e)}")

    def _call_gemini(self, prompt: str) -> str:
        """
        Make the actual Gemini API call using google-generativeai.
        """
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "The 'google-generativeai' package is missing. "
                "Please run: pip install google-generativeai"
            )

        try:
            genai.configure(api_key=self.gemini_key)
            model = genai.GenerativeModel(self.GEMINI_MODEL)
            
            # Simple retry logic for rate limits
            retries = 1
            while retries >= 0:
                try:
                    response = model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            max_output_tokens=self.MAX_TOKENS,
                            temperature=self.TEMPERATURE,
                        )
                    )
                    if hasattr(response, 'text'):
                        return response.text.strip()
                    else:
                        raise RuntimeError("Gemini API response contained no text.")
                except Exception as e:
                    if "429" in str(e) and retries > 0:
                        logger.warning("Rate limit hit. Retrying in 5 seconds...")
                        time.sleep(5)
                        retries -= 1
                    else:
                        raise e
            return "Failed to generate text after retries."
        except Exception as e:
            raise RuntimeError(f"Gemini API call failed: {str(e)}")

    def _call_openrouter(self, prompt: str) -> str:
        """
        Make the AI call via OpenRouter using the openai SDK.
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "The 'openai' package is missing. "
                "Please run: pip install openai"
            )

        try:
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.openrouter_key,
            )
            
            completion = client.chat.completions.create(
                model=self.openrouter_model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.MAX_TOKENS,
                temperature=self.TEMPERATURE,
            )
            
            if completion.choices:
                return completion.choices[0].message.content.strip()
            else:
                raise RuntimeError("OpenRouter response contained no choices.")
        except Exception as e:
            raise RuntimeError(f"OpenRouter call failed: {str(e)}")

    def _mock_response(self) -> str:
        """Return the pre-generated MOCK_NARRATION."""
        logger.info("Mock mode active: Returning static narration.")
        return MOCK_NARRATION

    @property
    def mode(self) -> str:
        """Return 'mock', 'gemini', or 'openrouter'."""
        if self.is_mock:
            return "MOCK"
        if self.openrouter_key:
            return "OPENROUTER"
        return "GEMINI"
