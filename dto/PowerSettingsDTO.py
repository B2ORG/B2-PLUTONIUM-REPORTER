import dataclasses
from pathlib import Path

@dataclasses.dataclass(frozen=True)
class PowerSettingsDTO:
    parsed: dict
    raw: str
