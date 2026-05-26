#!/bin/bash
set -e

echo "=== Aufgaben-Dashboard Installation ==="

# Python + Git installieren
echo "[1/4] Pakete installieren..."
apt update && apt install -y python3 python3-pip python3-venv git || {
    echo "FEHLER: Pakete konnten nicht installiert werden."
    echo "Tipp: Internetverbindung prüfen oder 'apt update' manuell ausführen."
    exit 1
}

# Repo klonen
echo "[2/4] Repository klonen..."
cd /opt
git clone https://github.com/dzeykop/taskboard.git || {
    echo "FEHLER: Repository konnte nicht geklont werden."
    echo "Tipp: Prüfe ob das Repo existiert und Public ist."
    exit 1
}
cd taskboard

# Virtual Environment
echo "[3/4] Python Umgebung einrichten..."
python3 -m venv venv || {
    echo "FEHLER: Virtual Environment konnte nicht erstellt werden."
    exit 1
}
source venv/bin/activate

# Dependencies installieren
echo "[4/4] Python-Pakete installieren..."
pip install -r requirements.txt || {
    echo "FEHLER: Python-Pakete konnten nicht installiert werden."
    echo "Tipp: requirements.txt prüfen."
    exit 1
}

mkdir -p uploads

echo ""
echo "================================"
echo "✓ Installation erfolgreich!"
echo "================================"
echo "Nächster Schritt: .env Datei anlegen"
echo "  cd /opt/taskboard"
echo "  nano .env"
