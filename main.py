from App import App
from pathlib import Path
from traceback import print_exc
import datetime as dt

VERSION = "1.1"

def main():
    print(f"B2 PLUTONIUM REPORTER V{VERSION}")

    (App(VERSION)
        .set_plutonium_path()
        .collect_relevant_logs()
        .collect_configs()
        .collect_file_hashes()
        .collect_hardware_data()
        .collect_event_log_entries()
        .collect_power_settings()
        .compose_report(Path.cwd() / f"b2-report-{int(dt.datetime.now().timestamp())}.zip")
    )
    input("Send the zip file to the person handling your issue")

if __name__ == "__main__":
    try:
        main()
    except Exception:
        print_exc()
    finally:
        input("\nPress Enter to exit")
