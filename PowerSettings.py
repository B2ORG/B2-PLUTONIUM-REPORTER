import subprocess, re
from dto.PowerSettingsDTO import PowerSettingsDTO


class PowerSettings:
    """
    Fully parses `powercfg /query` into a structured, human-readable format.
    Compatible with Windows 10 and Windows 11.
    """


    def collect(self) -> PowerSettingsDTO:
        raw = self._run_powercfg()
        return PowerSettingsDTO(self._parse_powercfg(raw), raw)

    # ---------------------------------------------------------
    # Run powercfg
    # ---------------------------------------------------------
    def _run_powercfg(self) -> str:
        try:
            proc = subprocess.run(
                ["powercfg", "/query"],
                capture_output=True,
                text=True,
                check=True,
            )
            return proc.stdout
        except Exception as e:
            return f"error: {e}"

    # ---------------------------------------------------------
    # Parse the entire output
    # ---------------------------------------------------------
    def _parse_powercfg(self, text: str) -> dict:
        schemes = {}
        current_scheme = None
        current_subgroup = None
        current_setting = None

        lines = text.splitlines()

        for line in lines:
            line = line.strip()

            # -------------------------------
            # Power Scheme
            # -------------------------------
            m = re.match(r"Power Scheme GUID: ([0-9a-fA-F\-]+)\s+\((.+)\)", line)
            if m:
                guid, name = m.groups()
                current_scheme = schemes.setdefault(guid, {
                    "name": name,
                    "subgroups": {}
                })
                current_subgroup = None
                current_setting = None
                continue

            # -------------------------------
            # Subgroup
            # -------------------------------
            m = re.match(r"Subgroup GUID: ([0-9a-fA-F\-]+)\s+\((.+)\)", line)
            if m:
                guid, name = m.groups()
                current_subgroup = current_scheme["subgroups"].setdefault(guid, {
                    "name": name,
                    "settings": {}
                })
                current_setting = None
                continue

            # -------------------------------
            # Setting
            # -------------------------------
            m = re.match(r"Power Setting GUID: ([0-9a-fA-F\-]+)\s+\((.+)\)", line)
            if m:
                guid, name = m.groups()
                current_setting = current_subgroup["settings"].setdefault(guid, {
                    "name": name,
                    "ac_value": None,
                    "dc_value": None,
                    "interpretation": None,
                })
                continue

            # -------------------------------
            # AC value
            # -------------------------------
            m = re.match(r"Current AC Power Setting Index: ([0-9a-fA-Fx]+)", line)
            if m and current_setting:
                current_setting["ac_value"] = m.group(1)
                continue

            # -------------------------------
            # DC value
            # -------------------------------
            m = re.match(r"Current DC Power Setting Index: ([0-9a-fA-Fx]+)", line)
            if m and current_setting:
                current_setting["dc_value"] = m.group(1)
                continue

        # After parsing, interpret values
        self._interpret_all(schemes)

        return schemes

    # ---------------------------------------------------------
    # Interpret values into human-readable form
    # ---------------------------------------------------------
    def _interpret_all(self, schemes: dict):
        for scheme in schemes.values():
            for subgroup in scheme["subgroups"].values():
                for setting in subgroup["settings"].values():
                    setting["interpretation"] = self._interpret_setting(setting)

    # ---------------------------------------------------------
    # Interpret a single setting
    # ---------------------------------------------------------
    def _interpret_setting(self, setting: dict) -> dict:
        """
        Converts hex values into human-readable meaning when possible.
        """
        name = setting["name"].lower()
        ac = setting["ac_value"]
        dc = setting["dc_value"]

        def hex_to_int(v):
            try:
                return int(v, 16)
            except:
                return None

        ac_i = hex_to_int(ac) if ac else None
        dc_i = hex_to_int(dc) if dc else None

        return {
            "ac": ac_i if ac_i is not None else ac,
            "dc": dc_i if dc_i is not None else dc,
        }
