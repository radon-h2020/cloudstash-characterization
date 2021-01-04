output "public_dns" {
  value       = aws_eip.ubuntu.public_dns
  description = "The public DNS name of the EC2 server instance. (aws_eip)"

  depends_on = [
    # Security group rule must be created before this IP address could
    # actually be used, otherwise the services will be unreachable.
    # aws_security_group_rule.ubuntu.local_access,
    aws_security_group.ubuntu
  ]
}

output "public_ip" {
  value       = aws_eip.ubuntu.public_ip
  description = "The public IP  of the EC2 server instance. (aws_eip)"

  depends_on = [
    # Security group rule must be created before this IP address could
    # actually be used, otherwise the services will be unreachable.
    # aws_security_group_rule.ubuntu.local_access,
    aws_security_group.ubuntu
  ]
}