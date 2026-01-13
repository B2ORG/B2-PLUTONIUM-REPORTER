import dataclasses
from pathlib import Path

@dataclasses.dataclass(frozen=True)
class FileConfigDTO:
    path: Path
