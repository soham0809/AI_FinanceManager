"""
Repository cleanup script - removes unnecessary test and temporary files
"""
import os
import glob

def cleanup_repository():
    """Remove unnecessary files to clean up the repository"""
    print("🧹 Cleaning up repository...")
    
    # Files to remove
    files_to_remove = [
        # Test files
        "test_auth_connection.py",
        "test_backend.py", 
        "test_flutter_connection.py",
        "test_flutter_connectivity.py",
        "test_sms_debug.py",
        "backend/test_auth_system.py",
        "backend/test_db_direct.py",
        "backend/test_password_fix.py",
        "backend/test_simple_registration.py",
        
        # Setup and fix scripts (keep only essential ones)
        "backend/create_auth_tables.py",
        "backend/fix_users_table.py",
        "backend/add_user_id_column.py",
        
        # Temporary network config (we have the centralized one now)
        "network_config.json",
    ]
    
    # Keep these essential files
    keep_files = [
        "update_ip.py",  # Essential for IP updates
        "backend/setup_auth_simple.py",  # Essential for setup
    ]
    
    removed_count = 0
    
    for file_path in files_to_remove:
        if file_path not in keep_files:
            full_path = os.path.join(os.getcwd(), file_path)
            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                    print(f"✅ Removed: {file_path}")
                    removed_count += 1
                except Exception as e:
                    print(f"❌ Failed to remove {file_path}: {e}")
            else:
                print(f"ℹ️  File not found: {file_path}")
    
    # Remove any __pycache__ directories
    pycache_dirs = []
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                pycache_dirs.append(os.path.join(root, dir_name))
    
    for pycache_dir in pycache_dirs:
        try:
            import shutil
            shutil.rmtree(pycache_dir)
            print(f"✅ Removed cache: {pycache_dir}")
            removed_count += 1
        except Exception as e:
            print(f"❌ Failed to remove {pycache_dir}: {e}")
    
    print(f"\n🎉 Cleanup completed! Removed {removed_count} files/directories")
    print("\n📋 Repository is now cleaner and more organized!")
    
    # Show remaining essential files
    print("\n📁 Essential files kept:")
    essential_files = [
        "update_ip.py - IP address update utility",
        "mobile_app/lib/config/network_config.dart - Central network configuration",
        "backend/setup_auth_simple.py - Database setup utility"
    ]
    
    for file_desc in essential_files:
        print(f"   ✅ {file_desc}")

if __name__ == "__main__":
    cleanup_repository()
