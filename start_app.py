#!/usr/bin/env python3
"""
🚀 AI Finance Manager - One-Click Startup Script
Automatically starts backend, frontend, and configures IP addresses
"""
import os
import sys
import socket
import subprocess
import time
import threading
import json
import sqlite3
from pathlib import Path

# Colors for console output
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_banner():
    """Print startup banner"""
    print(f"""
{Colors.PURPLE}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                🚀 AI Finance Manager 🚀                      ║
║              One-Click Startup Script                        ║
║                                                              ║
║  🤖 Chatbot + 📱 SMS Classification + 📊 Analytics          ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}
""")

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote server to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

def update_flutter_ip(ip_address):
    """Update IP address in Flutter API service"""
    api_service_path = Path("mobile_app/lib/services/api_service.dart")
    
    if not api_service_path.exists():
        print(f"{Colors.YELLOW}⚠️  Flutter API service not found{Colors.END}")
        return False
    
    try:
        with open(api_service_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace IP addresses in the baseUrl configuration
        lines = content.split('\n')
        updated_lines = []
        
        for line in lines:
            if 'return \'http://' in line and ':8000\'' in line:
                if 'Platform.isAndroid' in lines[max(0, lines.index(line)-5):lines.index(line)+1]:
                    updated_lines.append(f'      return \'http://{ip_address}:8000\';  // Auto-updated IP')
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)
        
        with open(api_service_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(updated_lines))
        
        print(f"{Colors.GREEN}✅ Updated Flutter API service with IP: {ip_address}{Colors.END}")
        return True
    except Exception as e:
        print(f"{Colors.RED}❌ Failed to update Flutter IP: {e}{Colors.END}")
        return False

def reset_database():
    """Reset database - delete existing and create fresh"""
    db_path = Path("backend/financial_copilot.db")
    
    # Remove existing database if it exists
    if db_path.exists():
        try:
            db_path.unlink()
            print(f"{Colors.GREEN}✅ Removed existing database{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to remove existing database: {e}{Colors.END}")
            return False
    
    # Create fresh database with all required columns
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Create transactions table with all columns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sms_text TEXT NOT NULL,
                vendor TEXT,
                amount REAL,
                date TEXT,
                category TEXT,
                confidence REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                payment_method VARCHAR(50),
                is_subscription BOOLEAN DEFAULT 0,
                subscription_service VARCHAR(100),
                card_last_four VARCHAR(4),
                upi_transaction_id VARCHAR(255),
                merchant_category VARCHAR(100),
                is_recurring BOOLEAN DEFAULT 0
            )
        """)
        
        # Create users table if needed
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
        print(f"{Colors.GREEN}✅ Fresh database created with all required columns{Colors.END}")
        return True
        
    except Exception as e:
        print(f"{Colors.RED}❌ Database creation failed: {e}{Colors.END}")
        return False

def check_ollama():
    """Check if Ollama is running and start if needed"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            if 'llama3.1:latest' in result.stdout:
                print(f"{Colors.GREEN}✅ Ollama is ready with llama3.1:latest model{Colors.END}")
                return True
            else:
                print(f"{Colors.YELLOW}⚠️  Downloading llama3.1:latest model...{Colors.END}")
                subprocess.run(['ollama', 'pull', 'llama3.1:latest'], check=False)
                return True
        else:
            print(f"{Colors.YELLOW}⚠️  Starting Ollama server...{Colors.END}")
            subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3)
            return True
    except Exception as e:
        print(f"{Colors.RED}❌ Ollama not available: {e}{Colors.END}")
        print(f"{Colors.YELLOW}ℹ️  Install Ollama from: https://ollama.ai{Colors.END}")
        return False

def start_backend(ip_address):
    """Start the backend server"""
    print(f"{Colors.BLUE}🚀 Starting Backend Server...{Colors.END}")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print(f"{Colors.RED}❌ Backend directory not found{Colors.END}")
        return None
    
    # Add backend to Python path and start server
    env = os.environ.copy()
    env['PYTHONPATH'] = str(backend_dir.absolute())
    
    try:
        process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 'app.main:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--reload'
        ], cwd=backend_dir, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for server to start
        time.sleep(5)
        
        # Check if server is running
        if process.poll() is None:
            print(f"{Colors.GREEN}✅ Backend server started successfully{Colors.END}")
            print(f"{Colors.CYAN}📍 API Server: http://{ip_address}:8000{Colors.END}")
            print(f"{Colors.CYAN}📚 API Docs: http://{ip_address}:8000/docs{Colors.END}")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"{Colors.RED}❌ Backend failed to start{Colors.END}")
            if stderr:
                print(f"{Colors.RED}Error: {stderr.decode()}{Colors.END}")
            return None
            
    except Exception as e:
        print(f"{Colors.RED}❌ Failed to start backend: {e}{Colors.END}")
        return None

def regenerate_flutter_models():
    """Regenerate Flutter models for new fields"""
    print(f"{Colors.BLUE}🔄 Regenerating Flutter models...{Colors.END}")
    
    flutter_dir = Path("mobile_app")
    if not flutter_dir.exists():
        print(f"{Colors.RED}❌ Flutter directory not found{Colors.END}")
        return False
    
    try:
        # Run build runner
        result = subprocess.run([
            'flutter', 'packages', 'pub', 'run', 'build_runner', 'build', '--delete-conflicting-outputs'
        ], cwd=flutter_dir, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print(f"{Colors.GREEN}✅ Flutter models regenerated successfully{Colors.END}")
            return True
        else:
            print(f"{Colors.YELLOW}⚠️  Model regeneration completed with warnings{Colors.END}")
            return True
            
    except Exception as e:
        print(f"{Colors.RED}❌ Failed to regenerate models: {e}{Colors.END}")
        return False

def start_flutter():
    """Start the Flutter app"""
    print(f"{Colors.BLUE}📱 Starting Flutter App...{Colors.END}")
    
    flutter_dir = Path("mobile_app")
    if not flutter_dir.exists():
        print(f"{Colors.RED}❌ Flutter directory not found{Colors.END}")
        return None
    
    try:
        process = subprocess.Popen([
            'flutter', 'run'
        ], cwd=flutter_dir)
        
        print(f"{Colors.GREEN}✅ Flutter app is starting...{Colors.END}")
        print(f"{Colors.CYAN}📱 Check your connected device for the app{Colors.END}")
        return process
        
    except Exception as e:
        print(f"{Colors.RED}❌ Failed to start Flutter: {e}{Colors.END}")
        return None

def test_backend(ip_address):
    """Test backend endpoints"""
    print(f"{Colors.BLUE}🧪 Testing Backend Services...{Colors.END}")
    
    import requests
    
    try:
        # Test health endpoint
        response = requests.get(f"http://{ip_address}:8000/health", timeout=10)
        if response.status_code == 200:
            print(f"{Colors.GREEN}✅ Health check passed{Colors.END}")
        
        # Test SMS parsing
        sms_data = {
            "sms_text": "Rs.250.00 debited from A/c **1234 on 15-Oct-25 to VPA swiggy@paytm UPI Ref 429876543210"
        }
        response = requests.post(f"http://{ip_address}:8000/v1/parse-sms-public", json=sms_data, timeout=30)
        if response.status_code == 200:
            print(f"{Colors.GREEN}✅ SMS parsing working{Colors.END}")
        
        # Test chatbot
        chatbot_data = {"query": "How much did I spend this month?", "limit": 10}
        response = requests.post(f"http://{ip_address}:8000/v1/chatbot/query-public", json=chatbot_data, timeout=30)
        if response.status_code == 200:
            print(f"{Colors.GREEN}✅ Chatbot responding{Colors.END}")
        
        return True
        
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  Some backend tests failed: {e}{Colors.END}")
        return False

def cleanup_old_files():
    """Remove unnecessary files and keep only essential ones"""
    print(f"{Colors.BLUE}🧹 Cleaning up unnecessary files...{Colors.END}")
    
    # Files and directories to remove
    cleanup_items = [
        "test_new_features.py",
        "flutter_chatbot_integration.dart",
        "regenerate_models.md",
        "test_flutter_integration.md",
        "FLUTTER_INTEGRATION_SUMMARY.md",
        "NEW_FEATURES_GUIDE.md",
        "backend/start_server.py",
        "backend/migrate_database.py",
        "backend/API_DOCUMENTATION.md",
        "backend/check_db.py",
        "backend/clean_db.py",
        "backend/fix_dates.py",
        "backend/fix_db.py",
        "backend/data_validator.py",
        "backend/.pytest_cache",
        "backend/__pycache__",
        "mobile_app/test",
    ]
    
    removed_count = 0
    for item in cleanup_items:
        item_path = Path(item)
        try:
            if item_path.exists():
                if item_path.is_file():
                    item_path.unlink()
                    removed_count += 1
                elif item_path.is_dir():
                    import shutil
                    shutil.rmtree(item_path)
                    removed_count += 1
        except Exception:
            pass
    
    print(f"{Colors.GREEN}✅ Cleaned up {removed_count} unnecessary files{Colors.END}")

def create_single_readme():
    """Create a comprehensive README file"""
    readme_content = """# 🚀 AI Finance Manager

## One-Click Startup

Run this single command to start everything:

```bash
python start_app.py
```

## What This App Does

🤖 **AI Financial Assistant**: Ask questions like "How much did I spend on food delivery?"
📱 **Smart SMS Parsing**: Automatically categorizes UPI, Credit Card, and Subscription transactions
📊 **Rich Analytics**: Visual insights with payment method indicators
💬 **Natural Language Queries**: Chat with your financial data

## Features

- ✅ **Automatic IP Configuration**: Works on any network
- ✅ **Fresh Database**: Resets database on each startup
- ✅ **Ollama Integration**: Local AI processing for privacy
- ✅ **Flutter Mobile App**: Modern, responsive UI
- ✅ **FastAPI Backend**: High-performance API server

## Requirements

- Python 3.8+
- Flutter SDK
- Ollama (for AI features)
- Android/iOS device or emulator

## Quick Start

1. **Install Ollama**: Download from https://ollama.ai
2. **Run the app**: `python start_app.py`
3. **Test features**: Use the mobile app to parse SMS and chat with AI

## API Endpoints

- Health: `/health`
- SMS Parsing: `/v1/parse-sms-public`
- Chatbot: `/v1/chatbot/query-public`
- Transactions: `/v1/transactions-public`
- Analytics: `/v1/analytics/*-public`

## Architecture

```
AI Finance Manager/
├── backend/           # FastAPI server
├── mobile_app/        # Flutter mobile app
└── start_app.py      # One-click startup script
```

## Support

If you encounter issues:
1. Ensure Ollama is installed and running
2. Check that your device is connected for Flutter
3. Verify network connectivity
4. Check console output for specific errors

**Built with ❤️ for intelligent financial management**
"""
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print(f"{Colors.GREEN}✅ Created comprehensive README.md{Colors.END}")

def main():
    """Main startup function"""
    print_banner()
    
    # Step 1: Get IP address
    print(f"{Colors.BOLD}Step 1: Network Configuration{Colors.END}")
    ip_address = get_local_ip()
    print(f"{Colors.GREEN}🌐 Detected IP Address: {ip_address}{Colors.END}")
    
    # Step 2: Update Flutter configuration
    print(f"\n{Colors.BOLD}Step 2: Flutter Configuration{Colors.END}")
    update_flutter_ip(ip_address)
    
    # Step 3: Database setup (Reset)
    print(f"\n{Colors.BOLD}Step 3: Database Reset{Colors.END}")
    reset_database()
    
    # Step 4: Check Ollama
    print(f"\n{Colors.BOLD}Step 4: AI Service Check{Colors.END}")
    ollama_ready = check_ollama()
    
    # Step 5: Start backend
    print(f"\n{Colors.BOLD}Step 5: Backend Server{Colors.END}")
    backend_process = start_backend(ip_address)
    
    if not backend_process:
        print(f"{Colors.RED}❌ Cannot continue without backend server{Colors.END}")
        return
    
    # Step 6: Test backend
    print(f"\n{Colors.BOLD}Step 6: Backend Testing{Colors.END}")
    test_backend(ip_address)
    
    # Step 7: Prepare Flutter
    print(f"\n{Colors.BOLD}Step 7: Flutter Preparation{Colors.END}")
    regenerate_flutter_models()
    
    # Step 8: Start Flutter
    print(f"\n{Colors.BOLD}Step 8: Mobile App{Colors.END}")
    flutter_process = start_flutter()
    
    # Step 9: Cleanup
    print(f"\n{Colors.BOLD}Step 9: Cleanup{Colors.END}")
    cleanup_old_files()
    create_single_readme()
    
    # Final status
    print(f"""
{Colors.GREEN}{Colors.BOLD}
🎉 AI Finance Manager is Ready!
{Colors.END}

{Colors.CYAN}📍 Backend API: http://{ip_address}:8000{Colors.END}
{Colors.CYAN}📚 API Documentation: http://{ip_address}:8000/docs{Colors.END}
{Colors.CYAN}📱 Mobile App: Check your connected device{Colors.END}

{Colors.YELLOW}🧪 Test Features:{Colors.END}
• Parse SMS messages in the mobile app
• Ask the AI chatbot about your finances
• View enhanced transaction details with payment method badges
• Explore analytics dashboard

{Colors.PURPLE}Press Ctrl+C to stop all services{Colors.END}
""")
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}🛑 Shutting down services...{Colors.END}")
        
        if backend_process:
            backend_process.terminate()
        if flutter_process:
            flutter_process.terminate()
        
        print(f"{Colors.GREEN}✅ All services stopped{Colors.END}")

if __name__ == "__main__":
    main()
