import gzip
import json
from collections import Counter
from pathlib import Path


LOG_DIRECTORY = Path("cloudtrail-logs")


def load_json(path):
    if path.name.endswith(".json.gz"):
        opener = gzip.open
    else:
        opener = open

    with opener(path, "rt", encoding="utf-8") as log_file:
        return json.load(log_file)


def extract_records(payload):
    if isinstance(payload, dict) and isinstance(payload.get("Records"), list):
        return [
            record
            for record in payload["Records"]
            if isinstance(record, dict)
        ]

    if isinstance(payload, list):
        return [
            record
            for record in payload
            if isinstance(record, dict)
        ]

    return []


def get_items(value):
    if isinstance(value, list):
        return value

    if isinstance(value, dict):
        items = value.get("items", [])
        if isinstance(items, list):
            return items

    return []

def get_case_insensitive(mapping, target_key):
    if not isinstance(mapping, dict):
        return None

    for key, value in mapping.items():
        if str(key).lower() == target_key.lower():
            return value

    return None

def contains_public_ssh_rule(event):
    parameters = event.get("requestParameters") or {}
    permissions = get_items(parameters.get("ipPermissions"))

    for permission in permissions:
        if not isinstance(permission, dict):
            continue

        protocol = str(permission.get("ipProtocol", "")).lower()

        try:
            from_port = int(permission.get("fromPort"))
            to_port = int(permission.get("toPort"))
        except (TypeError, ValueError):
            continue

        if protocol not in {"tcp", "6"}:
            continue

        if not from_port <= 22 <= to_port:
            continue

        ipv4_ranges = get_items(permission.get("ipRanges"))
        for ip_range in ipv4_ranges:
            if ip_range.get("cidrIp") == "0.0.0.0/0":
                return True

        ipv6_ranges = get_items(permission.get("ipv6Ranges"))
        for ip_range in ipv6_ranges:
            if ip_range.get("cidrIpv6") == "::/0":
                return True

    return False


def detect_security_change(event):
    event_name = event.get("eventName")
    event_source = event.get("eventSource")
    event_time = event.get("eventTime", "Unknown time")

    if (
        event_source == "ec2.amazonaws.com"
        and event_name == "AuthorizeSecurityGroupIngress"
        and contains_public_ssh_rule(event)
    ):
        return {
            "time": event_time,
            "severity": "HIGH",
            "status": "OPEN",
            "event": event_name,
            "finding": "Public SSH access was authorized",
        }

    if (
        event_source == "ec2.amazonaws.com"
        and event_name == "RevokeSecurityGroupIngress"
        and contains_public_ssh_rule(event)
    ):
        return {
            "time": event_time,
            "severity": "INFO",
            "status": "REMEDIATED",
            "event": event_name,
            "finding": "Public SSH access was revoked",
        }

    if (
        event_source == "s3.amazonaws.com"
        and event_name == "DeleteBucketPolicy"
    ):
        return {
            "time": event_time,
            "severity": "HIGH",
            "status": "OPEN",
            "event": event_name,
            "finding": "An S3 bucket policy was deleted",
        }

    if (
        event_source == "s3.amazonaws.com"
        and event_name == "PutBucketPolicy"
    ):
        return {
            "time": event_time,
            "severity": "REVIEW",
            "status": "CHANGED",
            "event": event_name,
            "finding": "An S3 bucket policy was created or updated",
        }

    if (
        event_source == "ec2.amazonaws.com"
        and event_name == "ModifyInstanceMetadataOptions"
    ):
        parameters = event.get("requestParameters") or {}
        
        metadata_request = get_case_insensitive(
            parameters,
            "ModifyInstanceMetadataOptionsRequest",
        )

        if not isinstance(metadata_request, dict):
            metadata_request = parameters

        http_tokens = str(
            get_case_insensitive(metadata_request, "HttpTokens") or ""
        ).lower()

        if http_tokens == "optional":
            return {
                "time": event_time,
                "severity": "HIGH",
                "status": "OPEN",
                "event": event_name,
                "finding": "IMDSv1 compatibility was enabled",
            }

        if http_tokens == "required":
            return {
                "time": event_time,
                "severity": "INFO",
                "status": "REMEDIATED",
                "event": event_name,
                "finding": "IMDSv2 enforcement was restored",
            }

    return None


def main():
    log_paths = list(LOG_DIRECTORY.rglob("*.json"))
    log_paths += list(LOG_DIRECTORY.rglob("*.json.gz"))

    files_read = 0
    records_read = 0
    failed_files = 0
    findings = []
    seen_event_ids = set()

    for log_path in sorted(log_paths):
        try:
            payload = load_json(log_path)
            records = extract_records(payload)

            files_read += 1
            records_read += len(records)

            for event in records:
                event_id = event.get("eventID")

                if event_id and event_id in seen_event_ids:
                    continue

                if event_id:
                    seen_event_ids.add(event_id)

                finding = detect_security_change(event)

                if finding:
                    findings.append(finding)

        except (OSError, json.JSONDecodeError):
            failed_files += 1
            print("One CloudTrail log file could not be read.")

    findings.sort(key=lambda item: item["time"])

    print(f"Files read: {files_read}")
    print(f"Records read: {records_read}")
    print(f"Unreadable files: {failed_files}")
    print(f"Security-relevant changes: {len(findings)}")

    if not findings:
        print("No security-relevant changes detected.")
        return

    print()

    for finding in findings:
        print(
            f"{finding['time']} | "
            f"{finding['severity']:<6} | "
            f"{finding['status']:<10} | "
            f"{finding['event']} | "
            f"{finding['finding']}"
        )

    severity_counts = Counter(
        finding["severity"]
        for finding in findings
    )

    print()
    print("Severity summary:")

    for severity in ("HIGH", "REVIEW", "INFO"):
        print(f"{severity}: {severity_counts.get(severity, 0)}")


if __name__ == "__main__":
    main()