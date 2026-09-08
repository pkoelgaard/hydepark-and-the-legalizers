output "instance_id" {
  value       = aws_instance.this.id
  description = "Production EC2 instance ID"
}

output "public_ip" {
  value       = aws_eip.this.public_ip
  description = "Production EC2 public IP address"
}

output "instance_public_dns" {
  value       = aws_instance.this.public_dns
  description = "Production EC2 public DNS"
}

output "security_group_id" {
  value       = aws_security_group.web.id
  description = "Production web security group ID"
}
