import json
import re
import os

def load_dictionary(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data['entries']

def parse_eva_file(path, page_id):
    lines = []
    with open(path, 'r') as f:
        for line in f:
            if f"<{page_id}" in line:
                # Prefer H transcription, fallback to F if H not present for that line ID?
                # Actually, let's just grab H lines.
                if ";H>" in line:
                    lines.append(line.strip())
    return lines

def clean_text(line):
    # Remove tags like <f87r...> and <-><!plant>
    # The format is <tag> text <tag>
    # We want the text part.
    # Example: <f87r.1,@P0;H>	poal!shsal.shocphor...
    
    parts = line.split('\t')
    if len(parts) < 2:
        return ""
    
    content = parts[1]
    # Remove trailing tags
    content = re.sub(r'<.*?>', '', content)
    # Remove inline tags if any (like <$>)
    content = re.sub(r'<.*?>', '', content)
    # Replace ! with . or just remove? ! usually separates words like . does in some contexts or denotes uncertainty? 
    # In IVTFF, ! can be a separator. . is definitely a separator.
    content = content.replace('!', '.')
    content = content.replace(',', '.')
    return content

def translate_word(word, dictionary):
    if word in dictionary:
        return dictionary[word].get('meaning', 'UNKNOWN')
    return None

def main():
    input_file = 'data/eva_ivtff.txt'
    dict_file = 'results/master_dictionary_v7_2.json'
    output_md = 'results/rosettes_translation.md'
    report_md = 'results/rosettes_report.md'
    
    dictionary = load_dictionary(dict_file)
    raw_lines = parse_eva_file(input_file, 'f87r')
    
    translations = []
    
    # Specific words to track
    special_words = {
        'aiin': 'Spring/Water',
        'okeol': 'Boil',
        'shedy': 'That/Which', # Or specific meaning from context
        'or': 'Direction/Gold',
        'ol': 'Direction/Oil',
        'daiin': 'Take Water',
        'qokeey': 'Cook/Process',
        'sh-': 'That/Which (Prefix)',
        't-': 'To (Prefix)'
    }
    
    found_specials = []
    
    with open(output_md, 'w') as f:
        f.write("# Rosettes (f87r) Translation\n\n")
        f.write("| Line | Original | Translation | Notes |\n")
        f.write("|------|----------|-------------|-------|\n")
        
        for line in raw_lines:
            # Extract line ID for reference
            line_id_match = re.search(r'<f87r\.(\d+).*?>', line)
            line_id = line_id_match.group(1) if line_id_match else "?"
            
            cleaned = clean_text(line)
            words = [w for w in cleaned.split('.') if w.strip()]
            
            line_trans = []
            line_notes = []
            
            for word in words:
                meaning = translate_word(word, dictionary)
                if meaning:
                    line_trans.append(f"**{meaning}** ({word})")
                else:
                    line_trans.append(word)
                
                # Check for special words
                if word in special_words:
                    found_specials.append((line_id, word, special_words[word]))
                    line_notes.append(f"{word}={special_words[word]}")
                
                # Check prefixes
                if word.startswith('sh') and word not in special_words:
                     # Maybe check if 'sh' is a prefix
                     pass

            trans_str = " ".join(line_trans)
            notes_str = ", ".join(line_notes)
            f.write(f"| {line_id} | {cleaned} | {trans_str} | {notes_str} |\n")

    # Generate Report
    with open(report_md, 'w') as f:
        f.write("# Rosettes (f87r) Analysis Report\n\n")
        f.write("## Special Terms Found\n\n")
        if found_specials:
            f.write("| Line | Word | Significance |\n")
            f.write("|------|------|--------------|\n")
            for item in found_specials:
                f.write(f"| {item[0]} | {item[1]} | {item[2]} |\n")
        else:
            f.write("No primary special terms (aiin, okeol, etc.) found in the checked lines.\n")
            
        f.write("\n## Analysis\n\n")
        f.write("### 1. Water Imagery (aiin, daiin)\n")
        # Count occurences
        aiin_count = sum(1 for x in found_specials if x[1] == 'aiin')
        daiin_count = sum(1 for x in found_specials if x[1] == 'daiin')
        f.write(f"- `aiin` (Spring/Water) count: {aiin_count}\n")
        f.write(f"- `daiin` (Take Water) count: {daiin_count}\n")
        
        if aiin_count > 0 or daiin_count > 0:
            f.write("The presence of water-related terms supports the hypothesis that this map relates to water sources or flows.\n")
        else:
            f.write("Absence of clear water terms might suggest a different focus, or they are encoded differently here.\n")

        f.write("\n### 2. Processing Terms (okeol, qokeey)\n")
        okeol_count = sum(1 for x in found_specials if x[1] == 'okeol')
        f.write(f"- `okeol` (Boil) count: {okeol_count}\n")
        
        f.write("\n### 3. Directional/Structural Terms\n")
        # Check for or, ol
        or_count = sum(1 for x in found_specials if x[1] == 'or')
        ol_count = sum(1 for x in found_specials if x[1] == 'ol')
        f.write(f"- `or` count: {or_count}\n")
        f.write(f"- `ol` count: {ol_count}\n")

        f.write("\n## Conclusion\n")
        f.write("Based on the translation...\n")

if __name__ == "__main__":
    main()
