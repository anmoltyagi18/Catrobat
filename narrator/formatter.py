import logging
import re
from typing import Dict, Any

logger = logging.getLogger(__name__)

class OutputFormatter:
    """
    Cleans, validates, and formats the narration output
    before writing to stdout or file.
    """

    MIN_SENTENCES = 2
    MAX_SENTENCES = 4

    def format(self, narration: str, mode: str, summary: Dict[str, Any]) -> str:
        """
        Format the final output as a pretty-printed block.
        """
        cleaned_text = self.clean(narration)
        self.warn_if_out_of_range(cleaned_text)

        event_count = summary.get("total_events", 0)
        high_severity = summary.get("high_severity_count", 0)

        # Build visual box
        width = 80
        header_text = f"  MARINE ECOSYSTEM NARRATION  [{mode}]"
        stats_text = f"  Events analyzed: {event_count} | High severity: {high_severity}"

        header = "╔" + "═" * (width - 2) + "╗\n"
        header += "║" + header_text.ljust(width - 2) + "║\n"
        header += "║" + stats_text.ljust(width - 2) + "║\n"
        header += "╠" + "═" * (width - 2) + "╣\n"
        
        # Word wrap narration
        content = "║" + " " * (width - 2) + "║\n"
        words = cleaned_text.split()
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > (width - 6):
                line_str = " ".join(current_line)
                content += "║  " + line_str.ljust(width - 6) + "  ║\n"
                current_line = [word]
                current_length = len(word)
            else:
                current_line.append(word)
                current_length += len(word) + 1
        
        if current_line:
            line_str = " ".join(current_line)
            content += "║  " + line_str.ljust(width - 6) + "  ║\n"
            
        content += "║" + " " * (width - 2) + "║\n"
        footer = "╚" + "═" * (width - 2) + "╝"

        return header + content + footer

    def clean(self, narration: str) -> str:
        """
        Strip extra whitespace, normalize newlines,
        and ensure the text ends with a period.
        """
        text = " ".join(narration.split())
        text = text.strip()
        if text and text[-1] not in ".!?":
            text += "."
        return text

    def count_sentences(self, text: str) -> int:
        """
        Count sentences by splitting on '. ', '! ', '? '.
        """
        # Split on sentence terminals followed by space or end of string
        sentences = re.split(r'[.!?](?:\s+|$)', text)
        # Filter out empty strings
        sentences = [s for s in sentences if s.strip()]
        return len(sentences)

    def warn_if_out_of_range(self, narration: str) -> None:
        """
        Log a warning if sentence count is outside [2, 4].
        """
        count = self.count_sentences(narration)
        if count < self.MIN_SENTENCES or count > self.MAX_SENTENCES:
            logger.warning(
                f"Narration length warning: {count} sentences found. "
                f"Expected between {self.MIN_SENTENCES} and {self.MAX_SENTENCES}."
            )
