import gzip
import json
from pathlib import Path

target_events = {"PutObject", "GetObject", "DeleteObject"}
matches = []

log_paths = list(Path(".").rglob("*.json"))
log_paths += list(Path(".").rglob("*.json.gz"))

for log_path in log_paths:
    try:
        if log_path.name.endswith(".json.gz"):
            log_file = gzip.open(log_path, "rt", encoding="utf-8")
        else:
            log_file = open(log_path, "r", encoding="utf-8")

        with log_file:
            records = json.load(log_file).get("Records", [])

        for event in records:
            if (
                event.get("eventSource") == "s3.amazonaws.com"
                and event.get("eventName") in target_events
            ):
                matches.append(
                    {
                        "time": event.get("eventTime"),
                        "event": event.get("eventName"),
                        "source": event.get("eventSource"),
                        "read_only": event.get("readOnly"),
                    }
                )

    except (OSError, json.JSONDecodeError):
        print("One downloaded file could not be read.")

if not matches:
    print("No matching S3 data events found in the downloaded logs.")
else:
    for match in sorted(matches, key=lambda item: item["time"] or ""):
        print(
            f"{match['time']} | "
            f"{match['event']} | "
            f"{match['source']} | "
            f"readOnly={match['read_only']}"
        )
