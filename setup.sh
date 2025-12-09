#!/usr/bin/env bash
# Source Code Risk Radar - Quick Setup Script

echo "=========================================="
echo "Source Code Risk Radar - Setup"
echo "=========================================="
echo ""

# Check Python
echo "✓ Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "⚠ Python 3 not found. Please install Python 3.9 or higher"
    echo "  Download from: https://www.python.org/downloads/"
    exit 1
fi

python_version=$(python3 --version | cut -d' ' -f2)
echo "  Found Python $python_version"
echo ""

# Create virtual environment
echo "✓ Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  Virtual environment created"
else
    echo "  Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "✓ Activating virtual environment..."
source venv/bin/activate
echo "  Activated"
echo ""

# Install requirements
echo "✓ Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "  Dependencies installed"
echo ""

# Run test analysis
echo "✓ Running test analysis..."
python main.py --use-dummy-data --output-format html
echo "  Test analysis complete"
echo ""

echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Open: reports/risk_dashboard_*.html"
echo "2. Review the interactive dashboard"
echo "3. Analyze your code: python main.py --repo-path /path/to/repo"
echo ""
echo "For more help, read QUICKSTART.md"
echo "=========================================="
