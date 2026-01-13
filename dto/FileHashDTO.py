import dataclasses

@dataclasses.dataclass(frozen=True)
class FileHashDTO:
    path: str
    hashes: dict[str, str]
    size: int
