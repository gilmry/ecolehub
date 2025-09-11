#!/bin/bash
# Script to run tests locally using virtual environment

cd "$(dirname "$0")/../backend"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
echo "📦 Installing dependencies..."
pip install -r requirements.stage4.txt -q 2>/dev/null || echo "Warning: Some dependencies failed to install"
pip install -r requirements.test.txt -q 2>/dev/null || echo "Warning: Test dependencies failed to install"

# Run tests based on argument
case "$1" in
    "unit")
        echo "🧪 Running unit tests..."
        python -m pytest test_simple.py test_core_functions.py -v -m unit
        ;;
    "coverage")
        echo "🧪 Running tests with coverage..."
        python -m pytest test_simple.py test_core_functions.py --cov=app --cov-report=term --cov-report=html
        ;;
    "simple")
        echo "🧪 Running simple tests..."
        python -m pytest test_simple.py test_core_functions.py -v
        ;;
    *)
        echo "🧪 Running all available tests..."
        python -m pytest test_simple.py test_core_functions.py -v
        ;;
esac

echo "✅ Test run complete!"