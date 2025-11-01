"""
Quick launcher for OraLake Streamlit App
Checks dependencies and starts the app
"""

import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required = {
        'streamlit': 'streamlit',
        'PIL': 'Pillow',
        'oracledb': 'oracledb'
    }
    
    missing = []
    
    for module, package in required.items():
        try:
            __import__(module)
            print(f"✅ {package} installed")
        except ImportError:
            missing.append(package)
            print(f"❌ {package} not found")
    
    return missing

def install_dependencies(packages):
    """Install missing dependencies"""
    print(f"\n📦 Installing missing packages: {', '.join(packages)}")
    
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install'
        ] + packages)
        print("✅ Installation complete!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False

def check_app_file():
    """Check if app.py exists"""
    app_path = Path("app.py")
    if not app_path.exists():
        print("❌ app.py not found in current directory!")
        print("Please run this script from the project root directory.")
        return False
    return True

def main():
    """Main launcher function"""
    print("=" * 60)
    print("🗄️  OraLake Streamlit App Launcher")
    print("=" * 60)
    print()
    
    # Check if app.py exists
    if not check_app_file():
        sys.exit(1)
    
    print("Checking dependencies...")
    print()
    
    # Check dependencies
    missing = check_dependencies()
    
    if missing:
        print()
        response = input(f"Install missing packages? (y/n): ").lower().strip()
        
        if response == 'y':
            if not install_dependencies(missing):
                sys.exit(1)
        else:
            print("\n⚠️  Please install missing packages manually:")
            print(f"   pip install {' '.join(missing)}")
            sys.exit(1)
    
    print()
    print("=" * 60)
    print("🚀 Launching Streamlit App...")
    print("=" * 60)
    print()
    print("The app will open in your browser at: http://localhost:8501")
    print("Press Ctrl+C to stop the server")
    print()
    
    # Launch streamlit
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'app.py'
        ])
    except KeyboardInterrupt:
        print("\n\n👋 App stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error launching app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()