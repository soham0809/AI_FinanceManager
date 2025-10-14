"""Simple IP address detection for mobile app connection"""
import socket
import subprocess

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return None

def get_network_info():
    """Get network information from ipconfig"""
    try:
        result = subprocess.run(['ipconfig'], capture_output=True, text=True, shell=True)
        return result.stdout
    except Exception:
        return "Could not get network information"

def main():
    print("=" * 60)
    print("IP ADDRESS DETECTION FOR MOBILE APP")
    print("=" * 60)
    
    # Get local IP
    local_ip = get_local_ip()
    if local_ip:
        print(f"Your Computer's IP Address: {local_ip}")
        print()
        print("MOBILE APP CONFIGURATION:")
        print("-" * 40)
        print("Edit: mobile_app/lib/services/api_service.dart")
        print()
        print("For Android Physical Device:")
        print(f"  return 'http://{local_ip}:8000';")
        print()
        print("For Android Emulator:")
        print("  return 'http://10.0.2.2:8000';")
        print()
        print("For iOS Simulator:")
        print("  return 'http://localhost:8000';")
        print()
    else:
        print("Could not detect local IP automatically")
    
    # Show network configuration
    print("NETWORK INTERFACES:")
    print("-" * 40)
    network_info = get_network_info()
    
    # Extract IPv4 addresses from ipconfig output
    lines = network_info.split('\n')
    for line in lines:
        if 'IPv4 Address' in line or 'IP Address' in line:
            print(f"  {line.strip()}")
    
    print()
    print("STARTUP INSTRUCTIONS:")
    print("-" * 40)
    print("1. Start Ollama: ollama serve")
    print("2. Start Backend: start_backend.bat")
    print("3. Update mobile app IP configuration")
    print("4. Start Mobile App: start_mobile_app.bat")
    print()
    print("Backend will be available at:")
    if local_ip:
        print(f"  - Local: http://localhost:8000")
        print(f"  - Network: http://{local_ip}:8000")
        print(f"  - API Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
