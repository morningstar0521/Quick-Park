#!/bin/bash
# One-time setup on a fresh Ubuntu EC2 instance. Run:  bash deploy/ec2-setup.sh
set -e

# 2 GB swap so the Vue build does not run out of memory on a 1 GB instance
if [ ! -f /swapfile ]; then
  sudo fallocate -l 2G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

# Docker + Docker Compose plugin
if ! command -v docker >/dev/null; then
  curl -fsSL https://get.docker.com | sudo sh
  sudo usermod -aG docker "$USER"
fi

echo "Done. Log out and SSH back in once, then run: docker compose up -d --build"
