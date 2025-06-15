#!/bin/bash

echo "🚀 Starting RWA Tokenization POC Deployment"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python $PYTHON_VERSION found, but Python $REQUIRED_VERSION or higher is required."
    exit 1
fi

print_success "Python $PYTHON_VERSION found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed. Please install pip3."
    exit 1
fi

# Create project structure
print_status "Creating project structure..."
mkdir -p app/{models,agents,utils}
mkdir -p {static/{css,js},templates,data,logs,uploads,tests}

# Create virtual environment
print_status "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install requirements
print_status "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    print_warning "requirements.txt not found. Installing basic dependencies..."
    pip install Flask Flask-SQLAlchemy Flask-CORS spacy nltk requests python-dateutil gunicorn pytest
fi

# Download NLP models
print_status "Downloading NLP models..."
python -m spacy download en_core_web_sm

# Download NLTK data
print_status "Downloading NLTK data..."
python -c "
import nltk
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('vader_lexicon')
print('NLTK data downloaded successfully!')
"

# Create necessary directories
print_status "Creating directories..."
mkdir -p logs data uploads static/css static/js templates

# Set permissions
print_status "Setting permissions..."
chmod +x deploy.sh
chmod +x run.sh 2>/dev/null || true

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file..."
    cat > .env << EOL
# Application Settings
SECRET_KEY=your-secret-key-change-this-in-production
FLASK_ENV=development
PORT=5000

# Database
DATABASE_URL=sqlite:///rwa_tokenization.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# File Uploads
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads
EOL
fi

# Initialize database
print_status "Initializing database..."
python -c "
import sys
sys.path.append('.')
try:
    from app.main import app, db
    with app.app_context():
        db.create_all()
    print('Database initialized successfully!')
except Exception as e:
    print(f'Database initialization error: {e}')
    print('This is normal if the code files are not yet in place.')
"

# Create run script if it doesn't exist
if [ ! -f "run.sh" ]; then
    print_status "Creating run script..."
    cat > run.sh << EOL
#!/bin/bash
echo "🚀 Starting RWA Tokenization POC..."

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export FLASK_APP=app/main.py
export FLASK_ENV=development

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the application
python app/main.py
EOL
    chmod +x run.sh
fi

# Create basic test file
if [ ! -f "tests/test_basic.py" ]; then
    print_status "Creating basic test file..."
    cat > tests/test_basic.py << EOL
import pytest
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_python_version():
    """Test that Python version is compatible"""
    assert sys.version_info >= (3, 8), "Python 3.8 or higher required"

def test_imports():
    """Test that basic imports work"""
    try:
        import flask
        import sqlalchemy
        import spacy
        import nltk
        assert True
    except ImportError as e:
        pytest.fail(f"Import error: {e}")

if __name__ == '__main__':
    test_python_version()
    test_imports()
    print("Basic tests passed!")
EOL
fi

# Run basic tests
print_status "Running basic tests..."
python tests/test_basic.py

print_success "Deployment completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Copy all the code components into their respective files"
echo "2. Run the application with: ./run.sh"
echo "3. Access the application at: http://localhost:5000"
echo ""
echo "📁 Project Structure:"
echo "├── app/"
echo "│   ├── main.py"
echo "│   ├── models/database.py"
echo "│   └── agents/"
echo "│       ├── nlp_agent.py"
echo "│       ├── verification_agent.py"
echo "│       └── tokenization_agent.py"
echo "├── static/"
echo "│   ├── css/style.css"
echo "│   └── js/app.js"
echo "├── templates/index.html"
echo "├── requirements.txt"
echo "├── config.py"
echo "└── .env"
echo ""
print_warning "Remember to change the SECRET_KEY in .env for production!"
echo ""
print_success "Ready to tokenize real-world assets! 🪙"