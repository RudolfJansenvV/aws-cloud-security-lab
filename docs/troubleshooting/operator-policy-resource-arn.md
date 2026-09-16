# Operator Policy Resource ARN Troubleshooting

## Context

A project-scoped IAM operator role was created to provide limited operational access to tagged EC2 instances.

The intended permissions allowed:

- Viewing EC2 and network configuration.
- Starting, stopping, and rebooting approved lab instances.
- No instance termination.
- No security-group modification.

Write access was restricted using the project tag:

```text
Project = AWSCloudSecurityLab
```

## Initial symptom

The IAM Policy Simulator returned Denied for `ec2:StartInstances`, even though the action was included in the operator policy.

The result details showed:
```text
Implicit deny due to no matching statements
```

The other simulated results behaved correctly:

| Action                              | Result  |
| ----------------------------------- | ------- |
| `ec2:DescribeInstances`             | Allowed |
| `ec2:TerminateInstances`            | Denied  |
| `ec2:AuthorizeSecurityGroupIngress` | Denied  |

## Investigation
### Incorrect simulator resource

The first simulator test used a friendly name after the instance/ portion of the resource ARN.

An EC2 instance ARN must contain the actual instance ID:
```
arn:aws:ec2:REGION:ACCOUNT_ID:instance/i-INSTANCE_ID
```
The simulator resource was corrected to use an instance ID beginning with i-.

### Incorrect managed-policy resource

The simulation remained denied after correcting the simulator resource.

The live customer-managed policy was then inspected. Its resource used the AWS account resource namespace:
```
arn:aws:account::ACCOUNT_ID:account/*
```
This resource could not match an EC2 StartInstances request because it described an account resource rather than an EC2 instance.

## Root cause

The permission statement used an incorrect resource ARN.

IAM could not match the requested EC2 instance against the policy resource, so the allow statement did not apply. Because no other statement allowed the action, AWS returned an implicit deny.

## Resolution

The managed policy resource was changed to the correct EC2 instance ARN format:
```
arn:aws:ec2:af-south-1:ACCOUNT_ID:instance/*
```

The policy continued to require:
```
"Condition": {
  "StringEquals": {
    "ec2:ResourceTag/Project": "AWSCloudSecurityLab"
  }
}
```

The corrected policy version was saved and set as the default version.

The simulator was then configured with:

- The specific lab instance ARN.
- The `ec2:ResourceTag/Project` context key.
- The value `AWSCloudSecurityLab`.

## Validation

After the correction, the simulator returned:

| Action                              | Expected | Result  |
| ----------------------------------- | -------- | ------- |
| `ec2:DescribeInstances`             | Allowed  | Allowed |
| `ec2:StartInstances`                | Allowed  | Allowed |
| `ec2:TerminateInstances`            | Denied   | Denied  |
| `ec2:AuthorizeSecurityGroupIngress` | Denied   | Denied  |

Evidence:

[Operator policy simulation](../evidence/07-project-operator-policy-simulation.png)

## Live role test

The `cloud-security-lab-operator-role` was assumed through an MFA-authenticated console session.

Using the operator role:

1. The tagged lab instance was visible.
2. The stopped instance was started successfully.
3. The running instance was stopped successfully.
4. The session was switched back to the bootstrap administrator identity.

This confirmed that AWS evaluated the real instance tag successfully outside the simulator.

## Additional console warnings

The EC2 console displayed some authorization warnings while using the operator role.

These occurred because the console performs additional background read requests beyond the actions needed to start and stop an instance. The warnings did not prevent the intended operations.

Instead of granting broad EC2 access, the missing read actions will be reviewed individually and added only if they provide a necessary operational benefit.

## Lessons learned

- An action, resource, and condition must all match before an allow statement applies.
- A valid-looking ARN can still identify the wrong AWS service or resource type.
- EC2 instance ARNs use instance IDs rather than friendly names.
- An implicit deny can indicate that no policy statement matched the request.
- Policy Simulator results should be followed by controlled live validation.
- Console usability permissions should be added iteratively rather than granting broad access.
