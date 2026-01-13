import wmi, ctypes
from ctypes import wintypes
from AbstractHardware import AbstractHardware
from dto.HadwareDTO import HardwareDTO


class HardwareWindows(AbstractHardware):
    def __init__(self):
        self._wmi = wmi.WMI()


    def report(self) -> HardwareDTO:
        return HardwareDTO(self.cpu(), self.gpu(), self.ram(), self.os(), self.display())


    def cpu(self) -> list[dict[str, str]]:
        try:
            return [
                {
                    "name": cpu.Name,
                    "cores": cpu.NumberOfCores,
                    "logical_processors": cpu.NumberOfLogicalProcessors,
                    "max_clock_mhz": cpu.MaxClockSpeed,
                    "manufacturer": cpu.Manufacturer,
                }
            for cpu in self._wmi.Win32_Processor()]
        except Exception as exc:
            print(f"Could not collect hardware data [CPU] with error {exc}")
            return []


    def gpu(self) -> list[dict[str, object]]:
        try:
            gpus = []

            for gpu in self._wmi.Win32_VideoController():
                vram = None
                if gpu.AdapterRAM is not None:
                    vram = gpu.AdapterRAM & 0xFFFFFFFF

                gpus.append({
                    "name": gpu.Name,
                    "driver_version": gpu.DriverVersion,
                    "video_ram_bytes": vram,
                    "video_processor": gpu.VideoProcessor,
                    "pnp_device_id": gpu.PNPDeviceID,
                })

            return gpus

        except Exception as exc:
            print(f"Could not collect hardware data [GPU] with error {exc}")
            return []


    def ram(self) -> list[dict[str, str]]:
        try:
            return [
                {
                    "capacity_bytes": mem.Capacity,
                    "speed_mhz": mem.Speed,
                    "manufacturer": mem.Manufacturer,
                    "part_number": mem.PartNumber.strip(),
                }
                for mem in self._wmi.Win32_PhysicalMemory()
            ]
        except Exception as exc:
            print(f"Could not collect hardware data [RAM] with error {exc}")
            return []


    def os(self) -> dict[str, str]:
        try:
            sys = self._wmi.Win32_OperatingSystem()[0]
            return {
                "name": sys.Caption,
                "version": sys.Version,
                "build_number": sys.BuildNumber,
                "architecture": sys.OSArchitecture,
            }
        except Exception as exc:
            print(f"Could not collect hardware data [OS] with error {exc}")
            return {}


    def display(self) -> list[dict[str, str]]:
        try:
            class DISPLAY_DEVICEW(ctypes.Structure):
                _fields_ = [
                    ("cb", wintypes.DWORD),
                    ("DeviceName", wintypes.WCHAR * 32),
                    ("DeviceString", wintypes.WCHAR * 128),
                    ("StateFlags", wintypes.DWORD),
                    ("DeviceID", wintypes.WCHAR * 128),
                    ("DeviceKey", wintypes.WCHAR * 128),
                ]


            class DEVMODEW(ctypes.Structure):
                _fields_ = [
                    ("dmDeviceName", wintypes.WCHAR * 32),
                    ("dmSpecVersion", wintypes.WORD),
                    ("dmDriverVersion", wintypes.WORD),
                    ("dmSize", wintypes.WORD),
                    ("dmDriverExtra", wintypes.WORD),
                    ("dmFields", wintypes.DWORD),
                    ("dmPositionX", wintypes.LONG),
                    ("dmPositionY", wintypes.LONG),
                    ("dmDisplayOrientation", wintypes.DWORD),
                    ("dmDisplayFixedOutput", wintypes.DWORD),
                    ("dmColor", wintypes.SHORT),
                    ("dmDuplex", wintypes.SHORT),
                    ("dmYResolution", wintypes.SHORT),
                    ("dmTTOption", wintypes.SHORT),
                    ("dmCollate", wintypes.SHORT),
                    ("dmFormName", wintypes.WCHAR * 32),
                    ("dmLogPixels", wintypes.WORD),
                    ("dmBitsPerPel", wintypes.DWORD),
                    ("dmPelsWidth", wintypes.DWORD),
                    ("dmPelsHeight", wintypes.DWORD),
                    ("dmDisplayFlags", wintypes.DWORD),
                    ("dmDisplayFrequency", wintypes.DWORD),
                ]

            user32 = ctypes.windll.user32

            monitors = []
            i = 0

            while True:
                display = DISPLAY_DEVICEW()
                display.cb = ctypes.sizeof(display)

                if not user32.EnumDisplayDevicesW(None, i, ctypes.byref(display), 0):
                    break

                # Skip mirroring drivers etc.
                if display.StateFlags & 0x1:  # DISPLAY_DEVICE_ATTACHED_TO_DESKTOP
                    devmode = DEVMODEW()
                    devmode.dmSize = ctypes.sizeof(devmode)

                    if user32.EnumDisplaySettingsW(display.DeviceName, -1, ctypes.byref(devmode)):
                        monitors.append({
                            "device_name": display.DeviceName,
                            "device_string": display.DeviceString,
                            "width": devmode.dmPelsWidth,
                            "height": devmode.dmPelsHeight,
                            "refresh_rate": devmode.dmDisplayFrequency,
                            "position_x": devmode.dmPositionX,
                            "position_y": devmode.dmPositionY,
                            "primary": bool(display.StateFlags & 0x4),  # DISPLAY_DEVICE_PRIMARY_DEVICE
                        })

                i += 1

            return monitors
        except Exception as exc:
            print(f"Could not collect hardware data [DISPLAY] with error {exc}")
            return []

