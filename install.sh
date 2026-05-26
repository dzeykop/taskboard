#!/bin/bash
set -e
echo "=== Aufgaben-Dashboard Installation ==="

apt update && apt install -y python3 python3-pip python3-venv git

cd /opt
git clone https://github.com/dzeykop/aufgaben-dashboard.git
cd aufgaben-dashboard

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

mkdir -p uploads

echo "=== Fertig! ==="
