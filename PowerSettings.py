import locale
import re
import subprocess
from ctypes import windll
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
                text=False,
                check=True,
            )
            stdout = proc.stdout if isinstance(proc.stdout, (bytes, bytearray)) else b""
            return self._decode_output(stdout)
        except Exception as e:
            return f"error: {e}"

    def _decode_output(self, data: bytes) -> str:
        if not data:
            return ""

        preferred = locale.getpreferredencoding(False)
        encodings = ["utf-8", preferred, "mbcs"]

        try:
            oem_cp = windll.kernel32.GetOEMCP()
            if oem_cp:
                encodings.append(f"cp{oem_cp}")
        except Exception:
            pass

        seen = set()
        unique_encodings = []
        for enc in encodings:
            if enc and enc.lower() not in seen:
                unique_encodings.append(enc)
                seen.add(enc.lower())

        for enc in unique_encodings:
            try:
                return data.decode(enc)
            except UnicodeDecodeError:
                continue

        return data.decode(unique_encodings[0] if unique_encodings else "utf-8", errors="replace")

    # ---------------------------------------------------------
    # Parse the entire output
    # ---------------------------------------------------------
    def _parse_powercfg(self, text: str) -> dict:
        if not isinstance(text, str):
            return {}

        schemes = {}
        current_scheme = None
        current_subgroup = None
        current_setting = None

        guid_line = re.compile(
            r"^(\s*).*?GUID:\s*([0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12})(?:\s+\((.*)\))?$"
        )
        ac_line = re.compile(r"\bAC\b.*?(0x[0-9a-fA-F]+)\b")
        dc_line = re.compile(r"\bDC\b.*?(0x[0-9a-fA-F]+)\b")

        for raw_line in text.splitlines():
            line = raw_line.rstrip()
            if not line.strip():
                continue

            m = guid_line.match(line)
            if m:
                indent, guid, name = m.groups()
                indent_size = len(indent)
                name = name or ""

                if indent_size == 0:
                    # Scheme is top-level in powercfg output.
                    current_scheme = schemes.setdefault(guid, {
                        "name": name,
                        "subgroups": {}
                    })
                    current_subgroup = None
                    current_setting = None
                    continue

                if indent_size <= 2:
                    if current_scheme is None:
                        continue
                    current_subgroup = current_scheme["subgroups"].setdefault(guid, {
                        "name": name,
                        "settings": {}
                    })
                    current_setting = None
                    continue

                if current_subgroup is None:
                    continue
                current_setting = current_subgroup["settings"].setdefault(guid, {
                    "name": name,
                    "ac_value": None,
                    "dc_value": None,
                    "interpretation": None,
                })
                continue

            if current_setting is None:
                continue

            m = ac_line.search(line)
            if m:
                current_setting["ac_value"] = m.group(1)
                continue

            m = dc_line.search(line)
            if m:
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
