from App import App

VERSION = "1.0"

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
        .compose_report()
    )
    input("Press ENTER to finish, send the zip file to the person handling your issue")

if __name__ == "__main__":
    main()
