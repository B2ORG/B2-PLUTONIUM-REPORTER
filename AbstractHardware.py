from abc import abstractmethod
from dto.HadwareDTO import HardwareDTO

class AbstractHardware:
    @abstractmethod
    def report(self) -> HardwareDTO: ...

    @abstractmethod
    def cpu(self) -> list[dict[str, str]]: ...

    @abstractmethod
    def gpu(self) -> list[dict[str, str]]: ...

    @abstractmethod
    def ram(self) -> list[dict[str, str]]: ...

    @abstractmethod
    def os(self) -> dict[str, str]: ...

    @abstractmethod
    def display(self) -> list[dict[str, str]]: ...
