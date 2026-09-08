variable "aws_region" {
  type        = string
  description = "AWS region"
  default     = "eu-north-1"
}

variable "instance_name" {
  type        = string
  description = "EC2 instance name"
  default     = "hydepark-prod"
}

variable "instance_type" {
  type        = string
  description = "EC2 instance type"
  default     = "t3.micro"
}

variable "root_volume_size_gb" {
  type        = number
  description = "Root EBS volume size"
  default     = 20
}

variable "allowed_ssh_cidr" {
  type        = list(string)
  description = "CIDR blocks allowed to SSH"
}

variable "public_key" {
  type        = string
  description = "SSH public key used for the EC2 key pair"
}

variable "enable_termination_protection" {
  type        = bool
  description = "Prevent accidental EC2 termination"
  default     = true
}

variable "common_tags" {
  type        = map(string)
  description = "Common resource tags"
  default = {
    ManagedBy   = "Terraform"
    Environment = "prod"
    Project     = "hydepark-and-the-legalizers"
  }
}
