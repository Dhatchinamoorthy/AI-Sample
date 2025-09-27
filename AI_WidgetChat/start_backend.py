#!/usr/bin/env python3
"""
Startup script for the AI Widget Chat backend
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Get the project root directory
    project_root = Path(__file__).parent
    backend_dir = project_root / "backend"
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Check if virtual environment exists
    venv_path = backend_dir / "venv"
    if not venv_path.exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    
    # Determine the correct Python executable
    if os.name == 'nt':  # Windows
        python_exe = venv_path / "Scripts" / "python.exe"
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:  # Unix-like
        python_exe = venv_path / "bin" / "python"
        pip_exe = venv_path / "bin" / "pip"
    
    # Install requirements
    print("Installing requirements...")
    subprocess.run([str(pip_exe), "install", "-r", "requirements.txt"], check=True)
    
    # Create .env file if it doesn't exist
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("Creating .env file...")
        with open(env_file, "w") as f:
            f.write("""# Database Configuration
DATABASE_URL=sqlite:///./database/ai_widget_chat.db

# Google Cloud / VertexAI Configuration
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
VERTEX_AI_LOCATION=us-central1

# External API Keys
OPENWEATHER_API_KEY=your-openweathermap-api-key
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-api-key
NEWS_API_KEY=your-newsapi-key

# Application Settings
SECRET_KEY=your-secret-key-change-in-production
DEBUG=true
CORS_ORIGINS=["http://localhost:4200", "http://127.0.0.1:4200"]

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379/0

# Widget Settings
WIDGET_CACHE_TTL=300
MAX_WIDGETS_PER_RESPONSE=5
""")
        print("Please edit .env file with your API keys and configuration.")
    
    # Create database directory
    database_dir = backend_dir / "database"
    database_dir.mkdir(exist_ok=True)
    
    # Start the server
    print("Starting the backend server...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([str(python_exe), "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"], check=True)
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    main()
