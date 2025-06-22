#!/usr/bin/env python3
"""
Setup script for Real Estate Data Pipeline
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_requirements():
    """Check if required tools are installed"""
    print("Checking requirements...")
    
    requirements = {
        'python': 'python --version',
        'docker': 'docker --version',
        'docker-compose': 'docker-compose --version'
    }
    
    missing = []
    for tool, command in requirements.items():
        try:
            result = subprocess.run(command.split(), capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ {tool}: {result.stdout.strip()}")
            else:
                missing.append(tool)
        except FileNotFoundError:
            missing.append(tool)
    
    if missing:
        print(f"\n❌ Missing requirements: {', '.join(missing)}")
        print("Please install the missing tools and try again.")
        return False
    
    print("✓ All requirements satisfied")
    return True


def setup_environment():
    """Set up environment file"""
    print("\nSetting up environment...")
    
    env_example = Path('.env.example')
    env_file = Path('.env')
    
    if not env_example.exists():
        print("❌ .env.example file not found")
        return False
    
    if env_file.exists():
        response = input("📝 .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Keeping existing .env file")
            return True
    
    shutil.copy(env_example, env_file)
    print("✓ Created .env file from template")
    
    print("\n📋 Please edit .env file with your configuration:")
    print("   - Add your API keys")
    print("   - Update database credentials if needed")
    print("   - Set SECRET_KEY for production")
    
    return True


def create_directories():
    """Create necessary directories"""
    print("\nCreating directories...")
    
    directories = [
        'logs',
        'data',
        'migrations/versions'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created {directory}/")
    
    return True


def setup_database():
    """Set up database using Docker Compose"""
    print("\nSetting up database...")
    
    try:
        # Start only PostgreSQL and Redis
        subprocess.run([
            'docker-compose', 'up', '-d', 'postgres', 'redis'
        ], check=True)
        
        print("✓ Database and Redis started")
        print("⏳ Waiting for services to be ready...")
        
        # Wait a bit for services to start
        import time
        time.sleep(10)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start database: {e}")
        return False


def install_dependencies():
    """Install Python dependencies"""
    print("\nInstalling Python dependencies...")
    
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], check=True)
        
        print("✓ Dependencies installed")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def run_demo():
    """Run the demo script"""
    print("\nRunning demo...")
    
    try:
        subprocess.run([sys.executable, 'demo_script.py'], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Demo failed: {e}")
        return False


def main():
    """Main setup function"""
    print("🏠 Real Estate Data Pipeline Setup")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path('requirements.txt').exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    steps = [
        ("Checking requirements", check_requirements),
        ("Setting up environment", setup_environment),
        ("Creating directories", create_directories),
        ("Installing dependencies", install_dependencies),
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            sys.exit(1)
    
    print("\n" + "=" * 40)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your API keys")
    print("2. Start the full system: docker-compose up -d")
    print("3. Access the API at: http://localhost:8000")
    print("4. View documentation at: http://localhost:8000/docs")
    print("\nOptional:")
    print("- Run demo: python demo_script.py")
    print("- View logs: docker-compose logs -f api")
    print("- Stop system: docker-compose down")


if __name__ == "__main__":
    main()