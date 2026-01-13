import datetime as dt
import re
from typing import Optional
from Game import Game
from PlutoniumFileType import PlutoniumFileType


class Crashdump:
    def __init__(self, revision: str, game: Game, datetime: dt.datetime, file: str, type: PlutoniumFileType):
        self._revision: str = revision
        self._game: Game = game
        self._datetime: dt.datetime = datetime
        self._file: str = file
        self._file_type: PlutoniumFileType = type


    def __str__(self) -> str:
        return f"Plutonium {self._revision} ({self._game}) on {self._datetime.strftime("%c")}"


    @classmethod
    def from_filename(cls, filename: str):
        elements = filename.split("-")
        datetime = dt.datetime(
            int(elements[3]),
            int(elements[4]),
            int(elements[5].split("_")[0]),
            int(elements[5].split("_")[1]),
            int(elements[6]),
            int(elements[7].split(".")[0] if "." in elements[7] else elements[7])
        )

        type = PlutoniumFileType.Crashdump
        if "minimal" in filename:
            type = PlutoniumFileType.CrashMinidump
        if filename.endswith(".txt"):
            type = PlutoniumFileType.CrashTxtDump

        return cls(elements[1], Game.from_pluto(elements[2]), datetime, filename, type)


    @staticmethod
    def get_common_exp():
        return re.compile(r"(plutonium-r[\d]{4,5}-t[\w]{3}-[\d]{4}-[\d]{2}-[\d]{2}_[\d]{2}-[\d]{2}-[\d]{2}).*")


    def matches_common(self, common: str) -> bool:
        return common in self._file


    def get_file(self) -> str:
        return self._file


    def get_file_type(self) -> PlutoniumFileType:
        return self._file_type


    def get_game(self) -> Game:
        return self._game
