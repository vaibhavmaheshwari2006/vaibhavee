import os
import zipfile

def zip_project():
    workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    zip_path = os.path.join(workspace_root, 'vaibhavmaheshwariee.zip')
    
    # List of files strictly necessary for the application to run
    essential_files = [
        ('src/app.py', 'src/app.py'),
        ('src/fingerprint.py', 'src/fingerprint.py'),
        ('src/database.py', 'src/database.py'),
        ('requirements.txt', 'requirements.txt'),
        ('packages.txt', 'packages.txt')
    ]
    
    print(f"Creating ZIP archive: {zip_path}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for local_path, zip_path_name in essential_files:
            file_path = os.path.join(workspace_root, local_path)
            if os.path.exists(file_path):
                zipf.write(file_path, zip_path_name)
                print(f"Added essential file: {zip_path_name}")
            else:
                print(f"Warning: File {local_path} not found, skipping.")
                
    print(f"ZIP archive successfully created: {zip_path} (size: {os.path.getsize(zip_path)} bytes)")

if __name__ == '__main__':
    zip_project()
