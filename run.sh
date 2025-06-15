#!/bin/bash

echo "🚀 Starting RWA Tokenization POC..."

# Activate virtual environment
source venv/Scripts/activate

# Set environment variables
export FLASK_APP=app/main.py
export FLASK_ENV=development

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the application
flask run
