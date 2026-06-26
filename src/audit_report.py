import pypdf

reader = pypdf.PdfReader('report.pdf')
full_text = ''
for page in reader.pages:
    full_text += page.extract_text() + '\n'

checks = {
    'Authors - Vaibhav Maheshwari': 'Vaibhav Maheshwari' in full_text,
    'Authors - Ayush Tiwari': 'Ayush Tiwari' in full_text,
    'Partner 1 label': 'Partner 1' in full_text,
    'Partner 2 label': 'Partner 2' in full_text,
    '32-bit integer mentioned': '32-bit' in full_text,
    'No 30-bit references remain': '30-bit' not in full_text,
    'Experimental Methodology Single-Peak': 'Experimental Methodology' in full_text,
    'Histogram figures present': 'histogram' in full_text.lower(),
    'Single mode screenshot caption': 'Single-Clip Mode' in full_text,
    'Batch mode screenshot caption': 'Batch Mode' in full_text,
    'Yesterday in sample CSV': 'Yesterday' in full_text,
    'filename + prediction columns': ('filename' in full_text and 'prediction' in full_text),
    'Pre-indexed DB note': ('Plug-and-Play' in full_text or 'pre-indexed' in full_text.lower()),
    'Streamlit live link': 'streamlit.app' in full_text,
    'GitHub source link': 'github.com' in full_text,
    'Q3 (A) section header': 'Q3 (A) Sonic Signatures' in full_text,
    'CQT improvement suggested': ('CQT' in full_text or 'Constant-Q' in full_text),
    'Noise robustness table': 'Gaussian Noise' in full_text,
    'Pitch Shift section': 'Pitch Shift' in full_text,
    'Time Stretch section': 'Time Stretch' in full_text,
    'Bit-packing equation present': 'Hash Integer' in full_text,
    'f1 bits 19-31 described': ('19-31' in full_text or 'bits 19' in full_text),
    'Fingerprints count (9539086)': '9,539,086' in full_text or '9539086' in full_text,
}

print('=== FINAL SUBMISSION AUDIT ===')
all_pass = True
for name, result in checks.items():
    status = 'PASS' if result else 'FAIL'
    if not result:
        all_pass = False
    print(f'  [{status}] {name}')

print()
print(f'Total pages: {len(reader.pages)}')
if all_pass:
    print('Overall: ALL CHECKS PASSED - Ready for submission!')
else:
    print('Overall: SOME CHECKS FAILED - See above')
