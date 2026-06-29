from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ConversationState:
    step: int = 0
    base_color: str = ""
    target_color: str = ""
    technique: str = ""
    water_test: str = ""

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "ConversationState":
        data = payload or {}
        step = data.get("step", 0)

        try:
            normalized_step = max(int(step), 0)
        except (TypeError, ValueError):
            normalized_step = 0

        return cls(
            step=normalized_step,
            base_color=str(data.get("baseColor", "") or ""),
            target_color=str(data.get("targetColor", "") or ""),
            technique=str(data.get("technique", "") or ""),
            water_test=str(data.get("waterTest", "") or ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "baseColor": self.base_color,
            "targetColor": self.target_color,
            "technique": self.technique,
            "waterTest": self.water_test,
        }


@dataclass(slots=True)
class ChatResult:
    response: str
    state: ConversationState
    restart: bool = False

