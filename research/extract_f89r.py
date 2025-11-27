import re
import os

def extract_f89r_text(input_path, output_path, version='H'):
    print(f"Reading {input_path}...")
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    extracted_lines = []
    
    # Regex to match lines for f89r and specific version
    # Format: <f89r...;V> text
    # We want f89r1 and f89r2
    pattern = re.compile(r"^<f89r.*?;{}>".format(version))
    
    for line in lines:
        if pattern.match(line):
            # Extract text part (after the tag)
            parts = line.strip().split('\t')
            if len(parts) > 1:
                text = parts[-1]
                # Clean text
                # Remove comments like <! ... >
                text = re.sub(r"<!.*?>", "", text)
                # Remove special markers like <->, <$>, etc.
                text = re.sub(r"<.*?>", "", text)
                # Remove certain characters if needed, but keep dots usually as word separators
                # Clean multiple dots or other artifacts if necessary
                text = text.strip()
                
                # Get the tag for context (e.g. line number or label)
                tag = parts[0]
                
                extracted_lines.append({'tag': tag, 'text': text})

    print(f"Extracted {len(extracted_lines)} lines.")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in extracted_lines:
            f.write(f"{item['tag']} {item['text']}\n")
            
    return extracted_lines

if __name__ == "__main__":
    input_file = "data/eva_ivtff.txt"
    output_file = "results/f89r_text.txt"
    extract_f89r_text(input_file, output_file)
