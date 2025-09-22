#!/usr/bin/env python3
"""
Script to help identify the correct IP address for mobile app connection
"""
import socket
import subprocess
import sys

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

def get_all_ips():
    """Get all network interfaces and their IPs"""
    try:
        result = subprocess.run(['ipconfig'], capture_output=True, text=True, shell=True)
        return result.stdout
    except Exception:
        return "Could not get network information"

def test_backend_connection(ip_address):
    """Test if backend is accessible on given IP"""
    import requests
    try:
        response = requests.get(f"http://{ip_address}:8000/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def main():
    print("=== IP Address Detection for Mobile App Connection ===\n")
    
    # Get local IP
    local_ip = get_local_ip()
    if local_ip:
        print(f"🔍 Detected Local IP: {local_ip}")
        
        # Test if backend is accessible on this IP
        if test_backend_connection(local_ip):
            print(f"✅ Backend is accessible on: http://{local_ip}:8000")
            print(f"\n📱 For PHYSICAL DEVICE, use this in api_service.dart:")
            print(f"   static const String baseUrl = 'http://{local_ip}:8000';")
        else:
            print(f"❌ Backend not accessible on: http://{local_ip}:8000")
    else:
        print("❌ Could not detect local IP")
    
    # Test localhost
    print(f"\n🔍 Testing localhost connection...")
    if test_backend_connection("localhost"):
        print("✅ Backend accessible on: http://localhost:8000")
        print("📱 For EMULATOR/SIMULATOR, use:")
        print("   Android Emulator: http://10.0.2.2:8000")
        print("   iOS Simulator: http://localhost:8000")
    else:
        print("❌ Backend not accessible on localhost")
        print("⚠️  Make sure backend server is running!")
    
    # Show network configuration
    print(f"\n🔍 Network Configuration:")
    network_info = get_all_ips()
    
    # Extract IPv4 addresses from ipconfig output
    lines = network_info.split('\n')
    for line in lines:
        if 'IPv4 Address' in line or 'IP Address' in line:
            print(f"   {line.strip()}")
    
    print(f"\n📋 Connection Guide:")
    print(f"   1. For Android Emulator: http://10.0.2.2:8000")
    print(f"   2. For iOS Simulator: http://localhost:8000")
    print(f"   3. For Physical Device: http://{local_ip}:8000" if local_ip else "   3. For Physical Device: Use your computer's IP")
    print(f"   4. For Web/Desktop: http://localhost:8000")
    
    print(f"\n🚀 Next Steps:")
    print(f"   1. Identify your testing environment (emulator/physical device)")
    print(f"   2. Update baseUrl in mobile_app/lib/services/api_service.dart")
    print(f"   3. Restart the mobile app")
    print(f"   4. Check console logs for connection attempts")

if __name__ == "__main__":
    main()
