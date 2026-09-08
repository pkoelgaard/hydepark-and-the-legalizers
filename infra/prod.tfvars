aws_region    = "eu-north-1"
instance_name = "hydepark-prod"
instance_type = "t3.micro"

root_volume_size_gb = 30

# Restrict SSH to your current public IP.
allowed_ssh_cidr = ["109.198.138.170/32"]

# Public key corresponding to the private key stored in GitHub Secret EC2_SSH_KEY.
# Replace the placeholder with the complete contents of ~/.ssh/id_rsa.pub.
public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDxfuGLFnjjalUCox6PlBkOAOssWzwH64Hr8hyLyXGxE4XSBrNm4jkl8ISGLMyVvmqs6IRMMXW0esfddO7iDVwPuExH8D4DQOTto9Ib6K5v+LmId5RZXSxDFtddMXHOIABaVdy5kZdwxBP7EosQACksy+IqSK51pOCbReMdyHQWOLbZaNh7iJkdIogcQdqCQwwTjB+0qIi7Q0qU1aIRvn3umwtaeOda7CIhfEK+1J0xSkkpHoT/A5GTUNYvNR8HKWunV7fFTkIzMJXc35QWFnIkm/gAyTOIzWKe8o7xVQk2EkrU+WxfVF84PFPSVh8IyVIlIm/BiCbU+Ekdkd0Cq2ph"

enable_termination_protection = true

common_tags = {
  ManagedBy   = "Terraform"
  Environment = "prod"
  Project     = "hydepark-and-the-legalizers"
}
