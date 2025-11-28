import re
import os

def clean_translation(input_file, output_file):
    print(f"Cleaning translation {input_file}...")
    
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found.")
        return

    clean_lines = []
    seen_lines = set()
    
    current_page_header = ""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Preserve Headers
            if line.startswith("#") or line.startswith("---"):
                clean_lines.append(line)
                continue
                
            # Handle Page Headers
            if line.startswith("## Page"):
                current_page_header = line
                clean_lines.append("\n" + line + "\n")
                seen_lines = set() # Reset dupe check per page
                continue
                
            # Skip empty lines
            if not line: continue
            
            # Remove tags: ?1,@P0, <$>, ?word
            # Regex to remove leading question marks and line IDs
            # Pattern: ^\?[\d,]+[@\+]P\d+\s+ -> Remove line ID
            cleaned = re.sub(r'^\?[\d,]+[@\+]P\d+\s+', '', line)
            
            # Remove tags like <f10r.1> or <->
            cleaned = re.sub(r'<.*?>', '', cleaned)
            
            # Remove ? prefix from unknowns
            cleaned = cleaned.replace(" ?", " ").replace("? ", " ")
            if cleaned.startswith("?"): cleaned = cleaned[1:]
            
            cleaned = cleaned.strip()
            
            if not cleaned: continue
            
            # Deduplication (Simple)
            # The raw output had identical lines for different transcribers
            if cleaned in seen_lines:
                continue
            
            seen_lines.add(cleaned)
            
            # Formatting: Sentence Case
            if cleaned:
                cleaned = cleaned[0].upper() + cleaned[1:]
                # Add period if missing
                if not cleaned.endswith(".") and not cleaned.endswith("]"):
                    cleaned += "."
            
            clean_lines.append(cleaned)

    with open(output_file, 'w', encoding='utf-8') as f:
        for l in clean_lines:
            f.write(l + "\n")
            
    print(f"Cleanup complete: {output_file}")

if __name__ == "__main__":
    clean_translation(
        "translated/THE_VOYNICH_MEDICAL_MANUAL.md",
        "translated/THE_VOYNICH_MEDICAL_MANUAL_CLEAN.md"
    )
