# Hyde Park and the Legalizers — production blueprint

This repository is a clean production-only blueprint based on the `cicd101` project.

## Architecture

- One AWS production EC2 instance in `eu-north-1`
- One Terraform state: `hydepark/terraform.tfstate`
- GitHub Actions deploys from `main` only
- GitHub OIDC for AWS authentication (no long-lived AWS credentials in GitHub)
- Nginx listens publicly on ports 80 and 443
- Flask/Gunicorn listens only on `127.0.0.1:5000`
- Port 5000 is **not** exposed in the AWS security group
- SSH is restricted to `allowed_ssh_cidr`
- Elastic IP is enabled so the public address remains stable

## Before first deployment

1. In AWS, make sure the GitHub OIDC provider exists. The account used by the old `cicd101` project already had one.
2. Deploy `aws/oidc-role.yaml` in CloudFormation and set `Repo` to `pkoelgaard/hydepark-and-the-legalizers`.
3. Note the role ARN and put it in `.github/workflows/deploy.yml`.
4. Create an EC2 key pair or provide the path to your local public key in `infra/prod.tfvars`.
5. Set your public SSH CIDR in `infra/prod.tfvars`.
6. Run Terraform from `infra/` using `config/backend-prod.hcl`.
7. Point `hydepark-and-the-legalizers.dk` and `www.hydepark-and-the-legalizers.dk` to the Elastic IP shown by Terraform.
8. After DNS resolves, SSH to the server and run:

   ```bash
   sudo /opt/hydepark/scripts/enable-https.sh
   ```

   This obtains a Let's Encrypt certificate and switches Nginx to HTTPS.

## GitHub Actions secrets

Create these repository secrets:

- `EC2_SSH_KEY` — private SSH key matching the public key used by Terraform
- `EC2_HOST` — the Elastic IP of the production instance

Do not commit private keys or passwords.

## Local Terraform commands

From `infra/`:

```bash
terraform init -backend-config=config/backend-prod.hcl
terraform plan -var-file=prod.tfvars
terraform apply -var-file=prod.tfvars
```

To destroy the production infrastructure intentionally, first set `enable_termination_protection = false` and then run:

```bash
terraform plan -destroy -var-file=prod.tfvars
terraform apply -destroy -var-file=prod.tfvars
```
