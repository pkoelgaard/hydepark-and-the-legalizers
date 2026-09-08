aws_region    = "eu-north-1"
instance_name = "hydepark-prod"
instance_type = "t3.micro"

root_volume_size_gb = 30

# Restrict SSH to your current public IP.
allowed_ssh_cidr = ["109.198.138.170/32"]

# Public key corresponding to the private key stored in GitHub Secret EC2_SSH_KEY.
# Replace the placeholder with the complete contents of ~/.ssh/id_rsa.pub.
public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDMoqzTJVe/ASrjQjMREVq9tswD/25UXTdQlfZJIWmofMdCH3+itqLU71lDNNciFbe5nXLfCdWdKc0YnS7iGOLSMph7OrqlCSToPFWchs0D4Z99FVkbJJInkk+JYbkOmKg7ZhauIbTfb1M9SW3dvCSTIVTX9XyBq1QEbelQ+41btSPRKhJ6nYGfvS1M4SkMMPuSlVYDBhLuTgeV6ysILifwDsAGRR/fgKFx6rKfqlG3UIphGvHk8RaCwyrBKU4O8miFPauVkxeBWq6YgPLQKUH5dF/U9q8sxKk2f7x2jwbA74HnqGlJs+xGBmlk4f109nxysvkqCm/zkZw9M2vN2WSjxjxnU6ZVxhGmFdPin8TJoANx7Qeo1UWtY1EYfNBcKi7iS7K/tXUkgl2qwRQUmJv6fGVe72CNvLOfproxQVe9Fmf4O4bvI8eYS6WbBUiUeo1I3GZg/iN2ksEoUsnKcs/rVuXEWpF2EYxUDve37kcAETLvVMbwr0QkQAQf+3JWFcM= peterkolgaard@peters-mbp.lan"

enable_termination_protection = true

common_tags = {
  ManagedBy   = "Terraform"
  Environment = "prod"
  Project     = "hydepark-and-the-legalizers"
}
