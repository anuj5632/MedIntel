from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List


class SeverityLevel(str, Enum):
    INFO = "INFO"
    ADVISORY = "ADVISORY"
    ALERT = "ALERT"
    EMERGENCY = "EMERGENCY"


@dataclass
class MessageTemplateContext:
    """
    Context that will be passed into the LLM prompt.
    """

    location_name: str
    severity: SeverityLevel
    reasons: List[str]
    languages: List[str]
    notes: str | None = None

    def build_system_instruction(self) -> str:
        return (
            "You are a public health communication assistant. "
            "Your job is to write SHORT, CLEAR public advisories for citizens. "
            "Avoid technical jargon. Always be calm and non-panicking, "
            "but honest about risks. Include 3–5 bullet points with actions."
        )

    def build_user_prompt(self, language: str) -> str:
        reasons_text = "\n".join(f"- {r}" for r in self.reasons) or "No specific reasons provided."
        notes_text = f"\nAdditional notes: {self.notes}" if self.notes else ""

        return (
            f"Write a public health message for residents of {self.location_name}.\n\n"
            f"Severity level: {self.severity.value}\n"
            f"Language: {language}\n"
            f"Reasons for this advisory:\n{reasons_text}\n"
            f"{notes_text}\n\n"
            "Requirements:\n"
            "- Start with a one-line summary.\n"
            "- Then provide 3–5 short bullet points of advice.\n"
            "- Mention vulnerable groups if relevant (children, elderly, people with asthma, etc.).\n"
            "- Keep the tone calm, practical and reassuring.\n"
            "- Limit the total length to about 120–180 words."
        )
