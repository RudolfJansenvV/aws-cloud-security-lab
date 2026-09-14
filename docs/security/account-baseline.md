# AWS Account Security Baseline

**Date established:** 14 September 2026  
**Environment:** Personal AWS cloud-security lab  
**Account plan:** AWS Free plan

## Purpose

This baseline was established before provisioning cloud resources. It reduces account-compromise risk, separates root access from daily administration, and provides visibility into unexpected cloud usage.

## Controls implemented

- Enabled multi-factor authentication for the AWS root user.
- Created the `CloudSecurityLabAdmins` IAM group.
- Assigned the AWS-managed `AdministratorAccess` policy to the bootstrap administrator group.
- Created a separate `rudolf-lab-admin` IAM user for routine administration.
- Enabled multi-factor authentication for the IAM administrator.
- Enabled IAM access to billing information.
- Configured a zero-spend AWS budget with email notifications.
- Created no root-user or IAM-user access keys.
- Stopped using the root user for routine console activity.

## Design decisions

### Separate root and daily access

The AWS root user has unrestricted account-level authority and is reserved for tasks that specifically require it. Routine administration is performed through a separate MFA-protected identity.

### Group-based permission management

Administrative permissions were assigned through an IAM group rather than attached directly to the user. This provides a central location for managing permissions and supports additional administrative identities if required.

### No programmatic credentials

No access keys were created during the initial account setup because the current work only requires console access. Programmatic access will use appropriately scoped credentials or temporary role-based access when it becomes necessary.

### Cost monitoring

A zero-spend budget was configured before deploying resources. This provides early notification if activity begins consuming AWS credits or exceeds applicable free usage limits.

## Current limitation

The bootstrap administrator currently has broad `AdministratorAccess` permissions. This is required for the initial account and lab setup but does not follow least privilege for normal workloads.

A restricted lab-operator policy or role will be created later with permissions limited to the AWS services required by this project.

## Verification

The following controls were manually verified:

- Root MFA reports as assigned.
- IAM administrator MFA reports as assigned.
- The administrator can successfully authenticate through the IAM sign-in page.
- The zero-spend budget reports as active.
- No programmatic access keys exist for the root or IAM administrator identities.
