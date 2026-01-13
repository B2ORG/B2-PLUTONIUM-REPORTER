import enum


class Game(enum.Enum):
    T4 = "t4"
    T5 = "t5"
    T6 = "t6"

    @classmethod
    def from_pluto(cls, pluto_game: str):
        return cls(pluto_game[:2])
