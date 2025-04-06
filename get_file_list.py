#!/usr/bin/env python3
import os

def get_pdf_file_list(directory):
    """
    Scans the given directory for PDF files,
    strips the '.pdf' extension, and returns a list of file names.
    """
    try:
        files = os.listdir(directory)
    except FileNotFoundError:
        print(f"Error: Directory '{directory}' does not exist.")
        return []

    # Filter for .pdf files and remove the extension
    pdf_files = [
        os.path.splitext(f)[0]
        for f in files
        if f.lower().endswith('.pdf')
    ]
    return pdf_files

if __name__ == '__main__':
    resources_dir = 'resources'
    file_list = get_pdf_file_list(resources_dir)
    
    if not file_list:
        print("No PDF files found or directory does not exist.")
    else:
        # Format output as a JavaScript array string with double quotes
        js_array = 'const fileList = [' + ', '.join(f'"{file}"' for file in file_list) + '];'
        print(js_array)
