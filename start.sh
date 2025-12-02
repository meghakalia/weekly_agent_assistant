#!/bin/bash
# Railway startup script

echo "Starting Weekly Grocery Agent Backend..."
echo "Python version:"
python --version

echo "Creating required directories..."
mkdir -p outputs
mkdir -p /tmp/outputs

echo "Starting gunicorn..."
exec gunicorn backend.main:app --bind 0.0.0.0:${PORT:-8080} --timeout 300 --workers 1 --log-level info
