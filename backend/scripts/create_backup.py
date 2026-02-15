import os
import zipfile
import datetime

def backup_project():
    # Source directory (current project root: smart_agri)
    source_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Destination zip file (parent directory of project)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    parent_dir = os.path.dirname(source_dir)
    zip_filename = os.path.join(parent_dir, f"smart_agri_backup_{timestamp}.zip")
    
    print(f"📦 Backing up '{source_dir}' to '{zip_filename}'...")
    
    # Folders to exclude
    EXCLUDE_DIRS = {
        'node_modules', 'venv', 'venv312', '.git', '__pycache__', 
        'dist', 'build', '.idea', '.vscode', 'coverage', '.pytest_cache',
        'data', 'backend/data'  # Exclude raw training data to save space
    }
    
    # Files to exclude
    EXCLUDE_FILES = {
        '.DS_Store', 'Thumbs.db', 'npm-debug.log'
    }

    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                # Modify dirs in-place to skip excluded directories
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                
                for file in files:
                    if file in EXCLUDE_FILES:
                        continue
                    
                    file_path = os.path.join(root, file)
                    # Create relative path for archive
                    arcname = os.path.relpath(file_path, source_dir)
                    
                    # Skip the zip file itself if it's being created inside (unlikely/safe check)
                    if file_path == zip_filename:
                        continue
                        
                    try:
                        zipf.write(file_path, arcname)
                    except PermissionError:
                        print(f"⚠️ Skipped (permission denied): {arcname}")
                    except OSError as e:
                        print(f"⚠️ Skipped (error): {arcname} - {e}")
                        
        print(f"\n✅ Backup created successfully!")
        print(f"📍 Location: {zip_filename}")
        print(f"📊 Size: {os.path.getsize(zip_filename) / (1024*1024):.2f} MB")
        
    except Exception as e:
        print(f"\n❌ Backup failed: {e}")

if __name__ == "__main__":
    backup_project()
