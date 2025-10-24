"""
Quick IP Update Script
Run this script to update the IP address across the entire project
"""
import json
import subprocess
import re

def get_current_ip():
    """Get current IP address from ipconfig"""
    try:
        result = subprocess.run(['ipconfig'], capture_output=True, text=True)
        output = result.stdout
        
        # Look for Wi-Fi adapter IP
        wifi_section = False
        for line in output.split('\n'):
            if 'Wireless LAN adapter Wi-Fi:' in line:
                wifi_section = True
            elif wifi_section and 'IPv4 Address' in line:
                # Extract IP address
                ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                if ip_match:
                    return ip_match.group(1)
        
        # Fallback: look for any IPv4 address
        ip_matches = re.findall(r'IPv4 Address.*?(\d+\.\d+\.\d+\.\d+)', output)
        if ip_matches:
            # Filter out localhost
            for ip in ip_matches:
                if not ip.startswith('127.'):
                    return ip
        
        return None
    except Exception as e:
        print(f"Error getting IP: {e}")
        return None

def update_network_config(new_ip):
    """Update the network configuration file"""
    config_path = "network_config.json"
    
    try:
        # Read current config
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Update IP
        old_ip = config['server_ip']
        config['server_ip'] = new_ip
        config['base_url'] = f"http://{new_ip}:8000"
        config['last_updated'] = "2025-10-20"
        
        # Write updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Updated network config: {old_ip} → {new_ip}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating config: {e}")
        return False

def update_flutter_config(new_ip):
    """Update Flutter network config"""
    config_path = "mobile_app/lib/config/network_config.dart"
    
    try:
        # Read current file
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Update IP address
        old_pattern = r"static const String serverIp = '[^']+'"
        new_content = re.sub(old_pattern, f"static const String serverIp = '{new_ip}'", content)
        
        # Write updated file
        with open(config_path, 'w') as f:
            f.write(new_content)
        
        print(f"✅ Updated Flutter config with IP: {new_ip}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating Flutter config: {e}")
        return False

def main():
    print("🔄 IP Address Update Tool")
    print("=" * 40)
    
    # Get current IP
    current_ip = get_current_ip()
    if not current_ip:
        print("❌ Could not detect current IP address")
        print("💡 Manually run 'ipconfig' and update the IP in:")
        print("   - mobile_app/lib/config/network_config.dart")
        return
    
    print(f"🌐 Detected IP Address: {current_ip}")
    
    # Update configurations
    success = True
    success &= update_network_config(current_ip)
    success &= update_flutter_config(current_ip)
    
    if success:
        print("\n🎉 IP address updated successfully!")
        print("\n📋 Next steps:")
        print("1. Restart your backend server")
        print("2. Hot restart your Flutter app (press 'R' in Flutter terminal)")
        print("3. Test the connection")
        print(f"\n🔗 New Base URL: http://{current_ip}:8000")
    else:
        print("\n❌ Some updates failed. Please check the errors above.")

if __name__ == "__main__":
    main()
