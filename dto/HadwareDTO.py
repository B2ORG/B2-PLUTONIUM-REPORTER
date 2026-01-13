import dataclasses

@dataclasses.dataclass(frozen=True)
class HardwareDTO:
    cpu: list[dict[str, str]]
    gpu: list[dict[str, str]]
    ram: list[dict[str, str]]
    os: dict[str, str]
    display: list[dict[str, str]]
