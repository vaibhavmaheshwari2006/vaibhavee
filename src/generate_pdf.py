import os
import re
import markdown
from fpdf import FPDF
from fpdf.enums import XPos, YPos

class MyPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, 'Audio Song Recognition System Report - Q3 Submission', new_x=XPos.RIGHT, new_y=YPos.TOP, align='R')
        self.ln(10)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')

def strip_tags_in_tables(html):
    def clean_cell(match):
        cell_tag_open = match.group(1)
        cell_content = match.group(2)
        cell_tag_close = match.group(3)
        # Strip any HTML tags (e.g. <strong>, <code>, etc.) inside the cell content
        cleaned_content = re.sub(r'<[^>]+>', '', cell_content)
        return cell_tag_open + cleaned_content + cell_tag_close
        
    # Process <td> elements with word boundaries \b
    html = re.sub(r'(<td\b[^>]*>)(.*?)(</td>)', clean_cell, html, flags=re.DOTALL)
    # Process <th> elements with word boundaries \b
    html = re.sub(r'(<th\b[^>]*>)(.*?)(</th>)', clean_cell, html, flags=re.DOTALL)
    return html

def convert():
    # Resolve paths relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.dirname(script_dir)
    
    md_path = os.path.join(workspace_root, 'report.md')
    pdf_path = os.path.join(workspace_root, 'report.pdf')
    
    if not os.path.exists(md_path):
        print(f"Error: Could not find report.md at {md_path}")
        return

    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Pre-process markdown text
    # 1. Clean up Math symbols to plain text
    md_text = md_text.replace('$$\\Delta \\tau = t_{db} - t_{query}$$', 'Time Difference (Delta) = t_db - t_query')
    md_text = md_text.replace('$$\\text{Hash Integer} = (f_1 \\ll 19) \\mid (f_2 \\ll 8) \\mid \\Delta t$$', 'Hash Integer = (f1 << 19) | (f2 << 8) | delta_t')
    md_text = md_text.replace('$\\Delta \\tau = t_{{db}} - t_{{query}}$', 'Delta = t_db - t_query')
    md_text = md_text.replace('$f_1$', 'f1').replace('$f_2$', 'f2').replace('$\\Delta t$', 'delta_t')

    # 2. Clean up blockquotes/alerts
    md_text = md_text.replace("> [!NOTE]", "**Note:**")

    # 3. Clean up backticks in tables
    lines = []
    for line in md_text.split('\n'):
        if '|' in line:
            line = line.replace('`', '')
        lines.append(line)
    md_text = '\n'.join(lines)

    # 4. Map Markdown image references to HTML image tags with explicit sizes
    md_text = md_text.replace('![Spectrogram](temp_plots/spectrogram.png)', '<img src="temp_plots/spectrogram.png" width="360" height="240" />')
    md_text = md_text.replace('![Constellation Map](temp_plots/constellation.png)', '<img src="temp_plots/constellation.png" width="360" height="240" />')
    md_text = md_text.replace('![Offset Alignment Histogram](temp_plots/histogram.png)', '<img src="temp_plots/histogram.png" width="450" height="225" />')

    # 5. Replace Mermaid diagram block with a clean textual/structural representation
    mermaid_block = """```mermaid
graph TD
    A[Raw Audio Input] --> B[Downsampling & STFT]
    B --> C[Constellation Map (2D Peak Detection)]
    C --> D[Combinatorial Hashing]
    D --> E[SQLite Database Query]
    E --> F[Offset Alignment Histogram (Voting)]
    F --> G[Matched Song Identification]
```"""
    
    mermaid_replacement = """**System Workflow Block Diagram:**
* **Raw Audio Input** -> **Downsampling & STFT**
* **Downsampling & STFT** -> **Constellation Map (2D Peak Detection)**
* **Constellation Map** -> **Combinatorial Hashing**
* **Combinatorial Hashing** -> **SQLite Database Query**
* **SQLite Database Query** -> **Offset Alignment Histogram (Voting)**
* **Offset Alignment Histogram** -> **Matched Song Identification**"""
    
    md_text = md_text.replace(mermaid_block, mermaid_replacement)

    # Convert markdown to html
    html = markdown.markdown(md_text, extensions=['tables'])

    # Clean HTML table tags
    html = strip_tags_in_tables(html)

    pdf = MyPDF()
    # Add Unicode fonts from Windows system fonts directory
    font_dir = r"C:\Windows\Fonts"
    pdf.add_font("Arial", "", os.path.join(font_dir, "arial.ttf"))
    pdf.add_font("Arial", "B", os.path.join(font_dir, "arialbd.ttf"))
    pdf.add_font("Arial", "I", os.path.join(font_dir, "ariali.ttf"))
    pdf.add_font("Arial", "BI", os.path.join(font_dir, "arialbi.ttf"))
    
    pdf.add_page()
    pdf.set_font('Arial', size=10)
    pdf.write_html(html)
    pdf.output(pdf_path)
    print(f"PDF generated successfully at: {pdf_path}")

if __name__ == '__main__':
    convert()
