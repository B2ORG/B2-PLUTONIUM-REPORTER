from pathlib import Path
from typing import Self, Optional
from collections.abc import Iterator, Callable
from Game import Game
import binascii, hashlib


class Plutonium:
    def __init__(self):
        self._root: Path

    def set_root(self, path: Path) -> Self:
        self._root = path
        return self

    def get_root(self) -> Path:
        return self._root

    def path_bin(self):
        return self._root / "bin"

    def path_crashdumps(self):
        return self._root / "crashdumps"

    def path_games(self):
        return self._root / "games"

    def path_launcher(self):
        return self._root / "launcher"

    def path_plugins(self):
        return self._root / "plugins"

    def path_storage(self):
        return self._root / "storage"

    def path_main_for(self, game: Game) -> Path:
        return self.path_storage() / game.value / "main"

    def path_mods_for(self, game: Game) -> Path:
        return self.path_storage() / game.value / "mods"

    def get_configs_for(self, game: Game) -> list[Path]:
        config_path = self.path_storage() / game.value
        return [cfg for cfg in Plutonium.dir_iterator(config_path, lambda x : x.suffix == ".cfg")]

    def without_root(self, path: Path) -> str:
        try:
            return str(path.relative_to(self._root))
        except ValueError:
            return str(path)

    def get_hashes(self, file: Path) -> dict[str, str]:
        return {
            "crc32": "0x" + format(binascii.crc32(file.read_bytes()) & 0xFFFFFFFF, "08X"),
            "sha1": hashlib.sha1(file.read_bytes(), usedforsecurity=False).hexdigest(),
            "sha256": hashlib.sha256(file.read_bytes(), usedforsecurity=False).hexdigest(),
        }

    @staticmethod
    def dir_iterator(path: Path, filter: Optional[Callable[[Path], bool]] = None) -> Iterator[Path]:
        for file in path.iterdir():
            if file.is_dir():
                yield from Plutonium.dir_iterator(file, filter)
            elif callable(filter) and not filter(file):
                continue
            else:
                yield file

    @staticmethod
    def is_static_file(file: Path) -> bool:
        if file.match("crashdumps"):
            return False
        if file.match("demos/*"):
            return False
        if file.suffix == ".cfg":
            return False
        if ".log" in file.name:
            return False
        return True
