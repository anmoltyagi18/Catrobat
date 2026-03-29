from typing import List, Dict, Any

class PromptBuilder:
    """
    Constructs a carefully engineered prompt for the Gemini model
    that produces a 2-4 sentence ecological narrative.
    """

    SYSTEM_CONTEXT = """You are MarineNarrator, an expert marine biologist
and science communicator embedded in a real-time ocean ecosystem simulation.
Your role is to translate raw simulation event logs into clear, engaging,
scientifically accurate 2-4 sentence summaries for a general audience.

Rules you must follow:
1. Always write exactly 2 to 4 sentences. No more, no less.
2. Mention at least two different organisms or environmental phenomena.
3. Identify one cause-and-effect relationship visible in the data.
4. Flag any ecological concern (coral stress, predator imbalance,
   temperature anomaly) if present in the events.
5. Write in present tense as if observing the simulation live.
6. Never use bullet points or lists. Pure narrative prose only.
7. Keep language accessible — no unexplained jargon."""

    def build(self, events: List[Dict[str, Any]], summary: Dict[str, Any]) -> str:
        """
        Build the full prompt string.
        Combines SYSTEM_CONTEXT + a formatted event section
        + a summary statistics section + the narration instruction.

        The event section must:
        - Show each event on its own line in human-readable form
        - Format: [timestamp] EVENT_TYPE | zone | organism (count) | details
        - Group events by zone for readability

        The summary section must show:
        - Total events, event type breakdown, zones affected,
          organisms involved, high-severity count

        End with this exact instruction:
        "Based on the simulation events above, write a 2-4 sentence
        ecological narrative summary following all rules stated."

        Returns the complete prompt string.
        """
        # Group events by zone
        zones = {}
        for event in events:
            zone = event.get("zone", "unknown")
            if zone not in zones:
                zones[zone] = []
            zones[zone].append(event)

        # Build events block
        events_block = "--- Simulation Events ---\n"
        for zone in sorted(zones.keys()):
            for event in zones[zone]:
                events_block += self._format_event_line(event) + "\n"
        
        # Build summary block
        summary_block = self._format_summary_block(summary)

        # Combine everything
        prompt = f"{self.SYSTEM_CONTEXT}\n\n"
        prompt += f"{events_block}\n"
        prompt += f"{summary_block}\n"
        prompt += "Based on the simulation events above, write a 2-4 sentence ecological narrative summary following all rules stated."
        
        return prompt

    def _format_event_line(self, event: Dict[str, Any]) -> str:
        """
        Format a single event as a human-readable line.
        Example output:
        [08:00 UTC] ORGANISM_SPAWNED | reef_zone_A | clownfish (12) | New clutch hatched near anemone host
        """
        timestamp = event.get("timestamp", "00:00:00Z")
        # Extract time part for brevity if desired, but here we'll use full timestamp
        # The prompt example shows [08:00 UTC], let's try to match it closely.
        time_part = timestamp.split("T")[-1].replace("Z", "")[:5]
        
        etype = str(event.get("event_type", "UNKNOWN")).upper()
        zone = event.get("zone", "unknown")
        organism = event.get("organism")
        count = event.get("count")
        details = event.get("details", "No details provided")

        organism_part = f"{organism}" if organism else "N/A"
        if count is not None:
             organism_part += f" ({count})"

        return f"[{time_part} UTC] {etype} | {zone} | {organism_part} | {details}"

    def _format_summary_block(self, summary: Dict[str, Any]) -> str:
        """
        Format the summary dict as a clean text block.
        Example:
        --- Simulation Summary ---
        Total events : 12
        Zones active : reef_zone_A, deep_zone_B, surface_zone
        Organisms    : clownfish, shark, plankton, coral
        High severity: 2 events
        Event types  : organism_spawned(4), temperature_anomaly(2), ...
        --------------------------
        """
        total = summary.get("total_events", 0)
        zones = ", ".join(summary.get("zones_affected", []))
        organisms = ", ".join(summary.get("organisms_involved", []))
        high_sev = summary.get("high_severity_count", 0)
        
        etypes = summary.get("event_types", {})
        etype_str = ", ".join([f"{k}({v})" for k, v in etypes.items()])

        block =  "--- Simulation Summary ---\n"
        block += f"Total events : {total}\n"
        block += f"Zones active : {zones}\n"
        block += f"Organisms    : {organisms}\n"
        block += f"High severity: {high_sev} events\n"
        block += f"Event types  : {etype_str}\n"
        block += "--------------------------"
        return block
