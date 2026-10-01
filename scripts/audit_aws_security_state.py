import argparse
import json
import subprocess
import sys
from collections import Counter


def run_aws_json(arguments, profile, region):
    command = [
        "aws",
        *arguments,
        "--profile",
        profile,
        "--region",
        region,
        "--output",
        "json",
        "--no-cli-pager",
    ]

    try:
        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as error:
        raise RuntimeError("AWS CLI is not installed or available.") from error
    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            "An AWS read-only command failed. "
            "Confirm the profile login and permissions."
        ) from error

    try:
        return json.loads(completed.stdout or "{}")
    except json.JSONDecodeError as error:
        raise RuntimeError(
            "AWS CLI returned an unreadable JSON response."
        ) from error


def get_project_instances(profile, region, project_tag):
    response = run_aws_json(
        [
            "ec2",
            "describe-instances",
            "--filters",
            f"Name=tag:Project,Values={project_tag}",
            (
                "Name=instance-state-name,"
                "Values=pending,running,stopping,stopped"
            ),
        ],
        profile,
        region,
    )

    instances = []

    for reservation in response.get("Reservations", []):
        instances.extend(reservation.get("Instances", []))

    return instances


def get_security_groups(instances, profile, region):
    group_ids = sorted(
        {
            group["GroupId"]
            for instance in instances
            for group in instance.get("SecurityGroups", [])
            if group.get("GroupId")
        }
    )

    if not group_ids:
        return []

    response = run_aws_json(
        [
            "ec2",
            "describe-security-groups",
            "--group-ids",
            *group_ids,
        ],
        profile,
        region,
    )

    return response.get("SecurityGroups", [])


def permission_allows_public_ssh(permission):
    protocol = str(permission.get("IpProtocol", "")).lower()

    if protocol == "-1":
        includes_ssh = True
    elif protocol in {"tcp", "6"}:
        try:
            from_port = int(permission.get("FromPort"))
            to_port = int(permission.get("ToPort"))
        except (TypeError, ValueError):
            return False

        includes_ssh = from_port <= 22 <= to_port
    else:
        return False

    if not includes_ssh:
        return False

    public_ipv4 = any(
        ip_range.get("CidrIp") == "0.0.0.0/0"
        for ip_range in permission.get("IpRanges", [])
    )

    public_ipv6 = any(
        ip_range.get("CidrIpv6") == "::/0"
        for ip_range in permission.get("Ipv6Ranges", [])
    )

    return public_ipv4 or public_ipv6


def count_public_ssh_rules(security_groups):
    return sum(
        1
        for group in security_groups
        for permission in group.get("IpPermissions", [])
        if permission_allows_public_ssh(permission)
    )


def evaluate_ec2_security(instances, security_groups):
    checks = []

    checks.append(
        {
            "name": "Project instance discovery",
            "passed": bool(instances),
            "detail": f"{len(instances)} matching instance(s)",
        }
    )

    if not instances:
        return checks

    public_ssh_rules = count_public_ssh_rules(security_groups)

    checks.append(
        {
            "name": "Public SSH exposure",
            "passed": public_ssh_rules == 0,
            "detail": (
                "No public TCP/22 rules detected"
                if public_ssh_rules == 0
                else f"{public_ssh_rules} public TCP/22 rule(s) detected"
            ),
        }
    )

    imdsv2_required = all(
        instance.get("MetadataOptions", {}).get("HttpTokens")
        == "required"
        for instance in instances
    )

    checks.append(
        {
            "name": "IMDSv2 enforcement",
            "passed": imdsv2_required,
            "detail": (
                "Required on all matching instances"
                if imdsv2_required
                else "One or more instances permit IMDSv1"
            ),
        }
    )

    metadata_enabled = all(
        instance.get("MetadataOptions", {}).get("HttpEndpoint")
        == "enabled"
        for instance in instances
    )

    checks.append(
        {
            "name": "Metadata endpoint",
            "passed": metadata_enabled,
            "detail": (
                "Enabled on all matching instances"
                if metadata_enabled
                else "Disabled or unknown on one or more instances"
            ),
        }
    )

    hop_limits = [
        instance.get("MetadataOptions", {}).get(
            "HttpPutResponseHopLimit"
        )
        for instance in instances
    ]

    secure_hop_limits = all(
        isinstance(limit, int) and 1 <= limit <= 2
        for limit in hop_limits
    )

    checks.append(
        {
            "name": "Metadata response hop limit",
            "passed": secure_hop_limits,
            "detail": (
                "All values are between 1 and 2"
                if secure_hop_limits
                else "Missing or greater than 2"
            ),
        }
    )

    no_key_pairs = all(
        not instance.get("KeyName")
        for instance in instances
    )

    checks.append(
        {
            "name": "EC2 key-pair exposure",
            "passed": no_key_pairs,
            "detail": (
                "No key pairs attached"
                if no_key_pairs
                else "One or more key pairs attached"
            ),
        }
    )

    return checks


def print_report(checks, instances):
    print("AWS EC2 Security State Audit")
    print()

    for check in checks:
        result = "PASS" if check["passed"] else "FAIL"
        print(
            f"[{result}] "
            f"{check['name']}: "
            f"{check['detail']}"
        )

    if instances:
        state_counts = Counter(
            instance.get("State", {}).get("Name", "unknown")
            for instance in instances
        )

        state_summary = ", ".join(
            f"{state}={count}"
            for state, count in sorted(state_counts.items())
        )

        print(f"[INFO] Instance states: {state_summary}")

    passed = sum(check["passed"] for check in checks)
    failed = len(checks) - passed

    print()
    print(f"Checks passed: {passed}")
    print(f"Checks failed: {failed}")

    return 0 if failed == 0 else 1


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "Audit the current EC2 security state without "
            "printing AWS resource identifiers."
        )
    )

    parser.add_argument(
        "--profile",
        default="lab-admin",
        help="AWS CLI profile name",
    )

    parser.add_argument(
        "--region",
        default="af-south-1",
        help="AWS Region",
    )

    parser.add_argument(
        "--project-tag",
        default="AWSCloudSecurityLab",
        help="Value of the EC2 Project tag",
    )

    return parser.parse_args()


def main():
    arguments = parse_arguments()

    try:
        instances = get_project_instances(
            arguments.profile,
            arguments.region,
            arguments.project_tag,
        )

        security_groups = get_security_groups(
            instances,
            arguments.profile,
            arguments.region,
        )

        checks = evaluate_ec2_security(
            instances,
            security_groups,
        )

        return print_report(checks, instances)

    except RuntimeError as error:
        print(f"[ERROR] {error}")
        return 2


if __name__ == "__main__":
    sys.exit(main())