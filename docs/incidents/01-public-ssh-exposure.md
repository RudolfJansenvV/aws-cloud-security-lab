# Incident 01 — Public SSH Security-Group Exposure

## Objective

Temporarily introduce an overly permissive SSH security-group rule, detect and investigate the configuration change, and restore the secure baseline.

This exercise demonstrates how a seemingly simple network change can expose an administrative service to the public internet.

## Misconfiguration

The lab EC2 security group will temporarily allow:

| Type | Protocol | Port | Source |
|---|---|---:|---|
| SSH | TCP | 22 | `0.0.0.0/0` |

This permits IPv4 traffic from any internet address to reach TCP port 22 when an associated resource is running and reachable.

## Safety controls

- The EC2 instance must remain stopped throughout the exposure.
- The instance has no EC2 key pair configured.
- The rule will be added only to the project EC2 security group.
- No additional ports will be opened.
- CloudTrail logging must remain enabled.
- The rule will be removed immediately after detection evidence is collected.
- The instance must not be started until the secure baseline is restored.
- No real credentials, sensitive data, or production resources are involved.

## Security risk

Allowing SSH from `0.0.0.0/0` unnecessarily exposes an administrative service to internet scanning, brute-force attempts, credential attacks, and exploitation of vulnerable SSH services.

Administrative access for this lab is provided through AWS Systems Manager Session Manager, so an inbound SSH rule is not operationally required.

## Expected CloudTrail activity

Creating the rule should generate the management event:

```text
AuthorizeSecurityGroupIngress
```
### Removing the rule should generate:
```
RevokeSecurityGroupIngress
```
## Detection plan

1. Verify the EC2 instance is stopped.
2. Verify the security group currently has no inbound rules.
3. Add the temporary public SSH rule.
4. Confirm the insecure rule appears in the security-group configuration.
5. Locate the change in CloudTrail Event history.
6. Record the event name, event time, identity type, source service, and affected resource without publishing sensitive identifiers.

## Remediation plan

1. Remove the 0.0.0.0/0 SSH rule.
2. Confirm that the security group again has no inbound rules.
3. Locate the corresponding revocation event in CloudTrail.
4. Verify the EC2 instance remains stopped.
5. Document the risk, detection evidence, remediation, and lessons learned.

## Evidence checklist
- [ ] Secure baseline before the change
- [ ] Temporary public SSH rule
- [ ] AuthorizeSecurityGroupIngress CloudTrail event
- [ ] Restored security-group baseline
- [ ] RevokeSecurityGroupIngress CloudTrail event
- [ ] Final confirmation that the instance remained stopped

## Status

Planned
