# EC2 Security Group Selection Issue

## Situation

While configuring the EC2 instance, the launch summary showed that the
`default` security group would be attached. The intended security group,
`cloud-security-lab-ec2-sg`, was not available for selection.

## Security concern

Launching with the default security group would not match the project’s
planned network controls. The instance should use a dedicated security
group with no inbound access and only the outbound connectivity required
for AWS Systems Manager.

## Investigation

Before launching the instance, I cancelled the deployment and checked the
available security groups.

I confirmed that the dedicated EC2 security group had not yet been created.

## Resolution

I created `cloud-security-lab-ec2-sg` inside `cloud-security-lab-vpc` with:

- No inbound rules
- Outbound HTTPS on TCP port 443 to `0.0.0.0/0`
- Project identification tags

I then returned to the EC2 launch configuration and selected the dedicated
security group instead of the default security group.

## Validation

Before launching, I verified that:

- The security group belonged to `cloud-security-lab-vpc`
- No inbound rules were configured
- The only outbound rule allowed HTTPS on TCP port 443
- The EC2 launch summary displayed `cloud-security-lab-ec2-sg`

## Lesson learned

AWS security groups are scoped to a VPC and should be created and validated
before launching dependent resources. Reviewing the final deployment summary
can prevent an instance from being launched with unintended network controls.
