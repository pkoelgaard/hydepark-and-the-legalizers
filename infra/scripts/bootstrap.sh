#!/bin/bash
set -euxo pipefail

dnf update -y
dnf install -y nginx git python3 python3-pip certbot python3-certbot-nginx

mkdir -p /opt/hydepark/scripts
chown -R ec2-user:ec2-user /opt/hydepark

python3 -m venv /opt/hydepark/venv
/opt/hydepark/venv/bin/pip install --upgrade pip

systemctl enable nginx
systemctl start nginx

cat > /etc/nginx/conf.d/hydepark.conf <<'NGINX'
server {
    listen 80;
    listen [::]:80;
    server_name hydepark-and-the-legalizers.com www.hydepark-and-the-legalizers.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX

nginx -t
systemctl reload nginx
