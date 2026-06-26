import os
import json
import base64
import requests

def compile_latex():
    workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tex_path = os.path.join(workspace_root, 'report.tex')
    pdf_output_path = os.path.join(workspace_root, 'report.pdf')
    plots_dir = os.path.join(workspace_root, 'temp_plots')
    
    if not os.path.exists(tex_path):
        print(f"Error: report.tex not found at {tex_path}")
        return
        
    print(f"Reading LaTeX source: {tex_path}")
    with open(tex_path, 'r', encoding='utf-8') as f:
        tex_content = f.read()
        
    # Build resources array
    resources = []
    
    # 1. Add main document
    resources.append({
        "main": True,
        "content": tex_content
    })
    
    # 2. Add all images in temp_plots/
    if os.path.exists(plots_dir):
        plot_files = [f for f in os.listdir(plots_dir) if f.endswith('.png')]
        print(f"Found {len(plot_files)} image assets in temp_plots/")
        for filename in plot_files:
            file_path = os.path.join(plots_dir, filename)
            # Relative path on the server-side filesystem (matching LaTeX paths)
            relative_path = f"temp_plots/{filename}"
            
            with open(file_path, 'rb') as img_f:
                img_data = img_f.read()
                img_b64 = base64.b64encode(img_data).decode('utf-8')
                
            resources.append({
                "path": relative_path,
                "file": img_b64
            })
            print(f"Added asset: {relative_path} (size: {len(img_data)} bytes)")
    else:
        print("Warning: temp_plots/ directory not found. Compiling without images.")
        
    # Setup request payload
    payload = {
        "compiler": "pdflatex",
        "resources": resources
    }
    
    url = "https://latex.ytotech.com/builds/sync"
    print(f"Sending compilation request to: {url}")
    
    try:
        response = requests.post(url, json=payload, timeout=90)
        
        # Check if content type is PDF
        content_type = response.headers.get('Content-Type', '')
        if 'application/pdf' in content_type:
            print(f"Compilation successful! Writing PDF to: {pdf_output_path}")
            with open(pdf_output_path, 'wb') as pdf_f:
                pdf_f.write(response.content)
            print("PDF file successfully saved.")
        else:
            # It's probably an error in JSON format
            try:
                err_data = response.json()
                print("Compilation failed. Error details:")
                print(json.dumps(err_data, indent=2))
            except Exception:
                print(f"Compilation failed with status code {response.status_code}.")
                print(response.text[:1000])
                
    except requests.exceptions.RequestException as e:
        print(f"HTTP request failed: {e}")

if __name__ == '__main__':
    compile_latex()
