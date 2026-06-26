import os
import zipfile

def zip_project():
    workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    zip_path = os.path.join(workspace_root, 'vaibhavmaheshwariee.zip')
    
    include_files = [
        'report.tex',
        'report.pdf',
        'requirements.txt'
    ]
    
    include_folders = [
        'src',
        'temp_plots'
    ]
    
    print(f"Creating ZIP archive: {zip_path}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Zip individual files
        for filename in include_files:
            file_path = os.path.join(workspace_root, filename)
            if os.path.exists(file_path):
                zipf.write(file_path, filename)
                print(f"Added file: {filename}")
            else:
                print(f"Warning: File {filename} not found, skipping.")
                
        # Zip directories
        for foldername in include_folders:
            folder_path = os.path.join(workspace_root, foldername)
            if os.path.exists(folder_path):
                for root, dirs, files in os.walk(folder_path):
                    # Skip __pycache__
                    if '__pycache__' in root:
                        continue
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Make path relative to workspace root
                        relative_path = os.path.relpath(file_path, workspace_root)
                        zipf.write(file_path, relative_path)
                        print(f"Added folder file: {relative_path}")
            else:
                print(f"Warning: Folder {foldername} not found, skipping.")
                
    print(f"ZIP archive successfully created: {zip_path} (size: {os.path.getsize(zip_path)} bytes)")

if __name__ == '__main__':
    zip_project()
