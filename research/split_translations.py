#!/usr/bin/env python3
"""
Split Full Translation into individual page markdown files.
Reads: results/voynich_full_translation_v7_4.md
Writes: translated/f<page_number>.md
"""

import os
import re
from pathlib import Path

INPUT_FILE = "results/voynich_full_translation_v7_4.md"
OUTPUT_DIR = "translated"

def main():
    print(f"Splitting {INPUT_FILE} into {OUTPUT_DIR}/...")
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory {OUTPUT_DIR}")

    current_page = None
    current_content = []
    
    try:
        with open(INPUT_FILE, 'r') as f:
            lines = f.readlines()
            
        for line in lines:
            # Detect page marker (e.g., "**f1r.1**: ...")
            # The file format uses "**<folio>.<line>**:"
            match = re.match(r'\*\*([a-z0-9]+v?r?)\.(\d+)\*\*:', line)
            
            if match:
                page = match.group(1)
                
                # If we hit a new page, save the previous one
                if page != current_page:
                    if current_page and current_content:
                        save_page(current_page, current_content)
                    
                    current_page = page
                    current_content = []
                    current_content.append(f"# Translated Page: {current_page}\n\n")
            
            # If we are tracking a page, add the line
            if current_page:
                current_content.append(line)
                
        # Save the last page
        if current_page and current_content:
            save_page(current_page, current_content)
            
        print("Done.")
        
    except FileNotFoundError:
        print(f"Error: Input file {INPUT_FILE} not found.")

def save_page(page, content):
    filename = os.path.join(OUTPUT_DIR, f"{page}.md")
    with open(filename, 'w') as f:
        f.writelines(content)
    print(f"Saved {filename}")

if __name__ == "__main__":
    main()
