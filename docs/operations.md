# Operations notes

## Ports

The EC2 security group intentionally exposes only:

- TCP 80 — public HTTP, used before/for HTTPS redirect
- TCP 443 — public HTTPS
- TCP 22 — SSH from `allowed_ssh_cidr`

TCP 5000 is **not** exposed. Gunicorn binds to `127.0.0.1:5000`, so only Nginx on the same server can reach it.

## HTTPS

After DNS for both the apex domain and `www` points to the Elastic IP, run:

```bash
sudo /opt/hydepark/scripts/enable-https.sh
```

Certbot configures the Nginx TLS certificate and HTTP-to-HTTPS redirect.

## Service checks

```bash
sudo systemctl status hydepark
sudo systemctl status nginx
curl http://127.0.0.1:5000/
```

## Terraform safety

This repository has only one Terraform environment: `prod`.
The production instance has termination protection enabled by default. To intentionally destroy it, disable termination protection in `prod.tfvars`, then run a destroy plan before applying it.
