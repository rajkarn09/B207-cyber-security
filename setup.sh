#!/bin/bash
# ============================================================
#  PhishGuard — One-Command Setup Script
#  B207 Cyber Security | Gisma University of Applied Sciences
#
#  Usage:
#    chmod +x setup.sh
#    ./setup.sh
#
#  What this script does:
#    1. Checks Python 3 is available
#    2. Creates a virtual environment
#    3. Installs all required Python libraries
#    4. Creates the required folders (db/, model/)
#    5. Trains the ML model and saves it to model/classifier.pkl
#    6. Initialises the SQLite database
# ============================================================

set -e  # Exit immediately if any command fails

echo ""
echo "=============================================="
echo "   PhishGuard — Setup & Initialisation"
echo "=============================================="

# ── Step 1: Check Python ────────────────────────
echo ""
echo "[1/6] Checking Python 3..."
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed. Please install it from https://python.org"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "      Found: $PYTHON_VERSION"

# ── Step 2: Virtual Environment ─────────────────
echo ""
echo "[2/6] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "      Virtual environment created."
else
    echo "      Virtual environment already exists — skipping."
fi

# Activate virtual environment
source venv/bin/activate
echo "      Activated: venv"

# ── Step 3: Install Dependencies ────────────────
echo ""
echo "[3/6] Installing required libraries from requirements.txt..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "      All libraries installed successfully."

# ── Step 4: Create Folders ──────────────────────
echo ""
echo "[4/6] Creating project directories..."
mkdir -p db model
echo "      Created: db/  model/"

# ── Step 5: Check Dataset ───────────────────────
echo ""
echo "[5/6] Checking for dataset..."

# Accept dataset path as argument or find it automatically
DATASET=""
if [ -n "$1" ]; then
    DATASET="$1"
elif [ -f "phishing_dataset.xlsx" ]; then
    DATASET="phishing_dataset.xlsx"
else
    # Look for any xlsx file in current directory
    DATASET=$(find . -maxdepth 1 -name "*.xlsx" | head -n 1)
fi

if [ -z "$DATASET" ]; then
    echo ""
    echo "  [!] No dataset found."
    echo "      Please place your dataset (phishing_dataset.xlsx) in this folder"
    echo "      or run:  ./setup.sh /path/to/your/dataset.xlsx"
    echo ""
    deactivate
    exit 1
fi

echo "      Dataset found: $DATASET"
export DATASET_PATH="$DATASET"

# ── Step 6: Train Model & Init Database ─────────
echo ""
echo "[6/6] Training model and initialising database..."
echo "      (This may take a few seconds...)"
echo ""

python3 - <<EOF
import os, sys
sys.path.insert(0, '.')
os.environ['DATASET_PATH'] = '$DATASET'

from phish_detector import PhishingDetector, init_db

# Train and save model
detector = PhishingDetector()
if not detector.train(dataset_path='$DATASET'):
    sys.exit(1)

# Init database
conn = init_db()
conn.close()

print("\n[✓] Model trained and saved to model/classifier.pkl")
print("[✓] Database initialised at db/phishing_analysis.db")
EOF

# ── Done ─────────────────────────────────────────
echo ""
echo "=============================================="
echo "   Setup Complete!"
echo "=============================================="
echo ""
echo "  To run PhishGuard:"
echo "    source venv/bin/activate"
echo "    python3 phish_detector.py"
echo ""
echo "  To specify a different dataset:"
echo "    DATASET_PATH=mydata.xlsx python3 phish_detector.py"
echo ""
