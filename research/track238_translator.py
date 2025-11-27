import json
import re
import os

def load_dictionary(path):
    print(f"Loading dictionary from {path}...")
    with open(path, 'r') as f:
        return json.load(f)

def extract_text(ivtff_path, target_folios):
    print(f"Extracting text from {ivtff_path} for folios {target_folios}...")
    extracted_lines = []
    
    # Regex to match the start of the line with folio and 'H' transcriber
    # Example: <f70r1.1,@Cc;H>
    # We look for lines starting with <f, followed by chars, then ending with ;H> before the content
    
    line_pattern = re.compile(r"<f([a-z0-9]+)[\.,].*;H>")
    
    with open(ivtff_path, 'r') as f:
        for line in f:
            match = line_pattern.match(line)
            if match:
                folio_code = match.group(1) # e.g., 70r1
                full_folio_name = "f" + folio_code
                
                # Check if matches any target
                is_target = False
                for tf in target_folios:
                    # Check if the extracted folio STARTS with the target (e.g. f70r1 starts with f70r)
                    if full_folio_name.startswith(tf):
                        is_target = True
                        break
                
                if is_target:
                    parts = line.split('>', 1)
                    if len(parts) > 1:
                        content = parts[1].strip()
                        # Remove comments <! ... >
                        content = re.sub(r'<!.*?>', '', content)
                        # Remove { ... }
                        content = re.sub(r'\{.*?\}', '', content)
                        
                        if content:
                            extracted_lines.append({
                                "folio": full_folio_name,
                                "tag": match.group(0).strip(),
                                "text": content
                            })
    print(f"Extracted {len(extracted_lines)} lines.")
    return extracted_lines

def translate_word(word, dictionary):
    # Remove punctuation for lookup
    clean_word = word.replace('.', '').replace(',', '').replace('!', '').replace('?', '').strip()
    
    entry = dictionary.get("entries", {}).get(clean_word)
    if entry:
        meaning = entry.get("meaning", "?")
        return f"{word} [{meaning}]"
    else:
        return word

def analyze_text(extracted_lines, dictionary):
    print("Translating and analyzing...")
    results = []
    summary_stats = {
        "total_lines": len(extracted_lines),
        "aiin_count": 0,
        "daiin_count": 0,
        "star_sentences": []
    }
    
    for line_data in extracted_lines:
        original_text = line_data["text"]
        # Normalize spaces
        normalized_text = original_text.replace('.', ' ')
        tokens = normalized_text.split()
        
        translated_tokens = []
        has_aiin_daiin = False
        
        for token in tokens:
            clean_token = token.replace(',', '').replace('!', '').replace('?', '').strip()
            if clean_token == 'aiin':
                summary_stats["aiin_count"] += 1
                has_aiin_daiin = True
            elif clean_token == 'daiin':
                summary_stats["daiin_count"] += 1
                has_aiin_daiin = True
                
            translated_tokens.append(translate_word(token, dictionary))
            
        translated_sentence = " ".join(translated_tokens)
        
        line_result = {
            "folio": line_data["folio"],
            "tag": line_data["tag"],
            "original": original_text,
            "translated": translated_sentence,
            "has_key_term": has_aiin_daiin
        }
        results.append(line_result)
        
        if has_aiin_daiin:
            summary_stats["star_sentences"].append(line_result)
            
    return results, summary_stats

def write_output(results, summary_stats, output_file, summary_file):
    print(f"Writing results to {output_file}...")
    with open(output_file, 'w') as f:
        f.write("# Zodiac Translation (f70r-f73v)\n\n")
        f.write("## Methodology\n")
        f.write("- **Dictionary**: v10.1 (Astral Shift)\n")
        f.write("- **Key Terms**: `aiin` (Star), `daiin` (The Star)\n\n")
        
        current_folio = ""
        for item in results:
            if item["folio"] != current_folio:
                f.write(f"\n### Folio {item['folio']}\n\n")
                current_folio = item["folio"]
            
            prefix = "⭐ " if item["has_key_term"] else ""
            f.write(f"**{item['tag']}**\n")
            f.write(f"> {item['original']}\n\n")
            f.write(f"{prefix}{item['translated']}\n\n")
            
    print(f"Writing summary to {summary_file}...")
    with open(summary_file, 'w') as f:
        f.write("# Track 238: Zodiac Translation Summary\n\n")
        f.write(f"- **Total Lines Processed**: {summary_stats['total_lines']}\n")
        f.write(f"- **`aiin` (Star) Count**: {summary_stats['aiin_count']}\n")
        f.write(f"- **`daiin` (The Star) Count**: {summary_stats['daiin_count']}\n\n")
        
        f.write("## Sentences with Astral Key Terms\n\n")
        for item in summary_stats["star_sentences"]:
             f.write(f"- **{item['folio']}** ({item['tag']}): {item['translated']}\n")

def main():
    dictionary_path = "results/dictionary_update_v10_1.json"
    ivtff_path = "data/eva_ivtff.txt"
    target_folios = ["f70r", "f70v", "f71r", "f71v", "f72r", "f72v", "f73r", "f73v"]
    
    dictionary = load_dictionary(dictionary_path)
    extracted_lines = extract_text(ivtff_path, target_folios)
    results, stats = analyze_text(extracted_lines, dictionary)
    
    write_output(results, stats, "results/zodiac_translation_v2.md", "results/track-238-results_summary.md")
    print("Done.")

if __name__ == "__main__":
    main()
