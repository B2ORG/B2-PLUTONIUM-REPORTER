import enum


class PlutoniumFileType(enum.Enum):
    Crashdump = 1
    CrashMinidump = 2
    CrashTxtDump = 3
    ConsoleLog = 4
    GameLog = 5
