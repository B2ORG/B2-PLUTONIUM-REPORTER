import dataclasses
from pathlib import Path
from PlutoniumFileType import PlutoniumFileType

@dataclasses.dataclass(frozen=True)
class FileLogDTO:
    path: Path
    type: PlutoniumFileType
