#!/bin/bash

echo "======================================"
echo "Face Attendance System Setup"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )(.+)')
echo "Found Python $python_version"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
echo "Virtual environment created!"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip
echo ""

# Install dependencies
echo "Installing dependencies..."
echo "This may take a few minutes..."
pip install -r requirements.txt
echo ""

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p data/faces
mkdir -p data/attendance
mkdir -p models
echo "Directories created!"
echo ""

echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "To run the application:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run the app: python app.py"
echo "3. Open browser: http://localhost:5000"
echo ""
echo "To deactivate virtual environment: deactivate"
echo ""
