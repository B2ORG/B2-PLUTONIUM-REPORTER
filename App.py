from pathlib import Path
from typing import Self, Optional

from dto.FileConfigDTO import FileConfigDTO
from dto.FileHashDTO import FileHashDTO
from dto.FileLogDTO import FileLogDTO
from dto.HadwareDTO import HardwareDTO
from AbstractHardware import AbstractHardware
from Crashdump import Crashdump
from Encoder import Encoder
from Game import Game
from HardwareWindows import HardwareWindows
from Plutonium import Plutonium
from PlutoniumFileType import PlutoniumFileType
from WindowsEventLog import WindowsEventLog

import os, sys, re, zipfile, json, uuid
import xml.etree.ElementTree as XML
import datetime as dt


class App:
    def __init__(self):
        self._runtime_alltime_events = "--all-events" in sys.argv

        self._plutonium: Plutonium = Plutonium()
        self._root: Path = Path(os.environ["localappdata"]) / "Plutonium"
        self._has_crashdumps: bool = False
        self._has_t4_logs: bool = False
        self._has_t5_logs: bool = False
        self._has_t6_logs: bool = False
        self._game: Optional[Game] = None
        self._logs: list[FileLogDTO] = []
        self._configs: list[FileConfigDTO] = []
        self._hashes: list[FileHashDTO] = []
        self._hardware: HardwareDTO
        self._events: list[XML.Element] = []


    def error_if(self, condition, message: str) -> None:
        if condition:
            input(message)
            sys.exit(0)


    def find_plutonium_path(self) -> Self:
        print("Detecting Plutonium path")
        if not self._root.exists():
            print("Default Plutonium path is missing. Press ENTER if reporter is currently placed in a Plutonium directory, or put in absolute path to Plutonium")
            try_path = input("> ")
            self._root = Path.cwd() if not try_path else Path(try_path)
            self.error_if(not self._root.exists(), f"The path {str(self._root)} does not exist. Quitting")

        self._plutonium.set_root(self._root)
        print(f"\tFound Plutonium path: {self._root}")
        return self


    def check_directory_structure(self) -> Self:
        print("Validating base Plutonium path structure")
        self.error_if(not self._plutonium.path_bin().exists(), "Missing 'bin' folder")
        self.error_if(not self._plutonium.path_games().exists(), "Missing 'games' folder")
        self.error_if(not self._plutonium.path_launcher().exists(), "Missing 'launcher' folder")
        self.error_if(not self._plutonium.path_storage().exists(), "Missing 'storage' folder")

        print("\tValidated presence of base Plutonium directories")

        self._has_crashdumps = bool(self._plutonium.path_crashdumps().exists() and len(list(self._plutonium.path_crashdumps().iterdir())))
        self._has_t4_logs = bool(self._plutonium.path_main_for(Game.T4).exists() and len(list(self._plutonium.path_main_for(Game.T4).glob("console.log*"))))
        self._has_t5_logs = bool(self._plutonium.path_main_for(Game.T5).exists() and len(list(self._plutonium.path_main_for(Game.T5).glob("console.log*"))))
        self._has_t6_logs = bool(self._plutonium.path_main_for(Game.T6).exists() and len(list(self._plutonium.path_main_for(Game.T6).glob("console_zm.log*"))))

        print(f"\tChecked for log presence: crashdumps={self._has_crashdumps} t4={self._has_t4_logs} t5={self._has_t5_logs} t6={self._has_t6_logs}")

        return self


    def collect_relevant_logs(self):
        print("Collecting Plutonium logs")
        self.error_if(not self._has_crashdumps and not self._has_t4_logs and not self._has_t5_logs and not self._has_t6_logs, "There are no logs to collect in your Plutonium directory")

        crashdumps: Optional[list[Crashdump]] = None
        if self._has_crashdumps:
            crashdumps = self._select_crashdump()

        if crashdumps is not None and len(crashdumps):
            for crashdump in crashdumps:
                self._logs.append(FileLogDTO(
                    self._plutonium.path_crashdumps() / crashdump.get_file(), crashdump.get_file_type()
                ))
            self._game = crashdumps[0].get_game()
            for file in self._plutonium.path_main_for(self._game).glob("*.log*"):
                type = PlutoniumFileType.ConsoleLog if file.match("console*.log") else PlutoniumFileType.GameLog
                self._logs.append(FileLogDTO(
                    self._plutonium.path_main_for(self._game) / file, type
                ))

            print(f"\tCollected {len(self._logs)} logs based on selected crashdump")
        else:
            print("Select in which game the problem/crash occured")
            print("1 - Call of Duty: World at War")
            print("2 - Call of Duty: Black Ops")
            print("3 - Call of Duty: Black Ops II")

            while True:
                selection = input("> ")
                if selection == "1":
                    self._game = Game.T4
                    break
                elif selection == "2":
                    self._game = Game.T5
                    break
                elif selection == "3":
                    self._game = Game.T6
                    break
                print("Incorrect selection, you must specify one of the 3 options listed above.")

            for file in self._plutonium.path_main_for(self._game).glob("*.log*"):
                type = PlutoniumFileType.ConsoleLog if file.match("console*.log") else PlutoniumFileType.GameLog
                self._logs.append(FileLogDTO(
                    self._plutonium.path_main_for(self._game) / file, type
                ))

            print(f"\tCollected {len(self._logs)} logs based on selected game")

        return self


    def collect_configs(self) -> Self:
        print("Collecting configs")
        configs: list[Path] = [
            self._plutonium.get_root() / "info.json",
            self._plutonium.path_storage() / Game.T5.value / "players" / "competitive-t5.json"
        ]
        configs.extend(self._plutonium.get_configs_for(Game.T4))
        configs.extend(self._plutonium.get_configs_for(Game.T5))
        configs.extend(self._plutonium.get_configs_for(Game.T6))

        self._configs = [FileConfigDTO(cfg) for cfg in configs if cfg.exists()]

        print(f"\tFound {len(self._configs)} configs")

        return self


    def collect_file_hashes(self) -> Self:
        print("Collecting file hashes")
        for path in [
            self._plutonium.path_bin(),
            self._plutonium.path_games(),
            self._plutonium.path_launcher(),
            self._plutonium.path_plugins(),
            self._plutonium.path_storage(),
        ]:
            if not path.exists():
                continue

            for file in Plutonium.dir_iterator(path, Plutonium.is_static_file):
                assert file.is_file(), f"{file} is not a file"
                self._hashes.append(FileHashDTO(
                    self._plutonium.without_root(file), self._plutonium.get_hashes(file), file.stat().st_size
                ))

        print(f"\tCollected {len(self._hashes)} hashes")

        return self


    def collect_hardware_data(self) -> Self:
        print("Collecting hardware info")
        hw: AbstractHardware = HardwareWindows()
        self._hardware = hw.report()
        print("\tCollected hardware report")
        return self


    def collect_event_log_entries(self) -> Self:
        print("Collecting event logs")
        event_log: WindowsEventLog = WindowsEventLog(self._plutonium.get_root(), self._runtime_alltime_events)
        self._events = event_log.collect()
        print(f"\tCollected {len(self._events)} events")
        return self


    def compose_report(self) -> Self:
        print(f"Generating incident report")
        report_path = Path.cwd() / f"b2-report-{int(dt.datetime.now().timestamp())}.zip"

        with zipfile.ZipFile(report_path, "x", compresslevel=9) as report:
            report.writestr("general.json", json.dumps({
                "root_path": self._root,
                "game": self._game.value,
                "created_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "crashdumps_detected": self._has_crashdumps,
                "file_hashes": [vars(dto) for dto in self._hashes],
                "hardware_info": vars(self._hardware)
            }, ensure_ascii=False, indent=4, cls=Encoder))

            report.mkdir("configs")
            config_dir = Path("configs")
            for cfg in self._configs:
                report.write(cfg.path, config_dir / self._plutonium.without_root(cfg.path))

            report.mkdir("logs")
            logs_dir = Path("logs")
            for log in self._logs:
                report.write(log.path, logs_dir / self._plutonium.without_root(log.path))

            report.mkdir("events")
            events_dir = Path("events")
            for event in self._events:
                report.writestr(str(events_dir / f"{uuid.uuid4().hex}.xml"), XML.tostring(event, xml_declaration=True))

        print(f"\tGenerated incident report at {report_path}")

        return self


    def _select_crashdump(self) -> Optional[list[Crashdump]]:
        dump_map: dict[int, Optional[Crashdump]] = {0: None}
        crashdumps: list[Crashdump] = []
        dump_games = set()

        print("Input a number representing the game that the crash/issue occured in and then press ENTER. If the game is not on the list, just press ENTER")
        for dump in self._plutonium.path_crashdumps().iterdir():
            common_file: Optional[re.Match] = re.search(Crashdump.get_common_exp(), str(dump))
            if common_file is None:
                continue
            crashdumps.append(Crashdump.from_filename(dump.name))
            common_file = common_file.group(1)

            if common_file not in dump_games:
                print(f"{len(dump_map)} - {common_file}")
                dump_map[len(dump_map)] = common_file
                dump_games.add(common_file)

        while True:
            selection = input("> ")
            if selection.isnumeric() and dump_map.get(int(selection)):
                file_opt = dump_map.get(int(selection))
                if not file_opt:
                    continue
                return list(filter(lambda x : x.matches_common(file_opt), crashdumps))
            if not selection:
                return None
            print("Incorrect input. Enter one of the numbers from the list above, or nothing if your game is not on the list")
