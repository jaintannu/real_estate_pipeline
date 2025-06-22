#!/usr/bin/env python3
"""
Setup script for Real Estate Analysis Notebook
Installs required packages and provides launch instructions
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install notebook requirements"""
    print("🔄 Installing notebook requirements...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements_notebook.txt"
        ])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def check_database():
    """Check database connection"""
    print("🔄 Checking database connection...")
    
    try:
        import psycopg2
        from sqlalchemy import create_engine
        
        # Try to connect
        connection_string = os.getenv(
            'DATABASE_URL', 
            'postgresql://postgres:password@localhost:5432/real_estate_db'
        )
        
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        
        print("✅ Database connection successful!")
        return True
    except Exception as e:
        print(f"⚠️ Database connection failed: {e}")
        print("   Make sure PostgreSQL is running and database exists")
        return False

def launch_jupyter():
    """Launch Jupyter notebook"""
    print("🚀 Launching Jupyter notebook...")
    
    try:
        # Change to the correct directory
        os.chdir(Path(__file__).parent)
        
        # Launch Jupyter
        subprocess.run([
            sys.executable, "-m", "jupyter", "notebook", 
            "Real_Estate_Analysis_Complete.ipynb"
        ])
    except KeyboardInterrupt:
        print("\n👋 Jupyter notebook closed")
    except Exception as e:
        print(f"❌ Failed to launch Jupyter: {e}")

def main():
    """Main setup function"""
    print("📊 Real Estate Analysis Notebook Setup")
    print("=" * 40)
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed - requirements installation error")
        return
    
    # Check database
    db_ok = check_database()
    
    print("\n📋 Setup Summary:")
    print(f"   Requirements: ✅ Installed")
    print(f"   Database: {'✅ Connected' if db_ok else '⚠️ Not connected'}")
    
    if not db_ok:
        print("\n⚠️ Database not connected - notebook will work with sample data")
    
    print("\n🚀 Ready to launch notebook!")
    
    # Ask user if they want to launch
    response = input("\nLaunch Jupyter notebook now? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        launch_jupyter()
    else:
        print("\n📝 To launch manually:")
        print("   cd real_estate_pipeline")
        print("   jupyter notebook Real_Estate_Analysis_Complete.ipynb")

if __name__ == "__main__":
    main()