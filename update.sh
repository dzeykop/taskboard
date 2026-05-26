#!/bin/bash
set -e
cd /opt/aufgaben-dashboard
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --quiet
systemctl restart aufgaben-bot aufgaben-web
echo "Update erfolgreich!"
