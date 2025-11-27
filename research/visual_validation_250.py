import re
import json
import os
from collections import defaultdict

# Constants
EVA_FILE = 'data/eva_ivtff.txt'
DICT_FILE = 'results/dictionary/dictionary.json'
REPORT_FILE = 'results/visual_validation_report.md'

RED_PAGES = ['25v', '39v', '57v']
BLUE_PAGES = ['13r', '101v', '34v']

TARGET_WORDS = {
    'or': {'color': 'Red', 'target_pages': RED_PAGES, 'opp_pages': BLUE_PAGES, 'desc': 'Red / Hot (Verified)'},
    'ol': {'color': 'Blue', 'target_pages': BLUE_PAGES, 'opp_pages': RED_PAGES, 'desc': 'Blue / Wet (Verified)'}
}

def parse_eva_data(filepath):
    """Parses the EVA data to get word counts per page."""
    page_word_counts = defaultdict(lambda: defaultdict(int))
    
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                match = re.match(r'<f(\d+[rv]).*?>\s*(.*)', line)
                if match:
                    page_id = match.group(1)
                    content = match.group(2)
                    words = re.split(r'[.\s]+', content)
                    
                    for word in words:
                        word = word.strip()
                        if word:
                            page_word_counts[page_id][word] += 1
                            
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

    return page_word_counts

def analyze_correlations(page_counts):
    results = {}
    
    for word, info in TARGET_WORDS.items():
        target_color = info['color']
        target_pages = info['target_pages']
        opp_pages = info['opp_pages']
        
        # 1. Counts on Target vs Opposite
        count_target = 0
        count_opp = 0
        
        for p in target_pages:
            if p in page_counts:
                count_target += page_counts[p][word]
                
        for p in opp_pages:
            if p in page_counts:
                count_opp += page_counts[p][word]
        
        ratio_opp = count_target / count_opp if count_opp > 0 else (float('inf') if count_target > 0 else 0)
        
        # 2. Comparison vs Global Average
        # Calculate total words in target pages vs total words in all other pages
        total_words_target = sum(sum(page_counts[p].values()) for p in target_pages if p in page_counts)
        
        other_pages = [p for p in page_counts if p not in target_pages] # All non-target pages (including opp)
        total_words_other = sum(sum(page_counts[p].values()) for p in other_pages)
        count_other = sum(page_counts[p][word] for p in other_pages)
        
        freq_target = count_target / total_words_target if total_words_target > 0 else 0
        freq_other = count_other / total_words_other if total_words_other > 0 else 0
        
        ratio_global = freq_target / freq_other if freq_other > 0 else 0
        
        # Verification Logic:
        # Verify if:
        # A) Strongly preferred over Opposite (Ratio > 1.5)
        # B) OR Strongly preferred over Global Average (Ratio > 2.0) AND Count is significant (>10)
        
        verified = False
        reasons = []
        
        if count_target >= 3:
            if ratio_opp > 1.5:
                verified = True
                reasons.append(f"Preferred over {info['opp_pages'][0]}... pages ({ratio_opp:.1f}x)")
            
            if ratio_global > 1.5: # Lowered threshold to 1.5 for global too
                verified = True
                reasons.append(f"High frequency vs global avg ({ratio_global:.1f}x)")
        
        results[word] = {
            'color': target_color,
            'count_target': count_target,
            'count_opp': count_opp,
            'ratio_opp': ratio_opp,
            'ratio_global': ratio_global,
            'verified': verified,
            'reasons': reasons
        }
        
    return results

def update_dictionary(analysis_results):
    try:
        if not os.path.exists(DICT_FILE):
            print(f"Dictionary file not found: {DICT_FILE}")
            return

        with open(DICT_FILE, 'r') as f:
            data = json.load(f)
            
        updated = False
        for word, result in analysis_results.items():
            if result['verified']:
                new_def = TARGET_WORDS[word]['desc']
                note = f"Visual validation: " + ", ".join(result['reasons'])
                
                entry_data = {
                    "definition": new_def,
                    "confidence": 1.0,
                    "notes": note
                }

                if word in data:
                    if isinstance(data[word], dict):
                        data[word].update(entry_data)
                    else:
                        data[word] = entry_data
                else:
                    data[word] = entry_data
                    
                updated = True
                print(f"Updated {word} in dictionary.")
        
        if updated:
            with open(DICT_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            print("Dictionary saved.")
        else:
            print("No dictionary updates needed.")
            
    except Exception as e:
        print(f"Error updating dictionary: {e}")

def generate_report(analysis_results):
    with open(REPORT_FILE, 'w') as f:
        f.write("# Visual Validation Report (Track 250)\n\n")
        f.write("## Methodology\n")
        f.write("Checked frequency of `or` (Red candidate) and `ol` (Blue candidate).\n")
        f.write("Criteria: Ratio vs Opposite Color > 1.5 OR Ratio vs Global Average > 1.5.\n\n")
        
        f.write("## Results\n\n")
        f.write("| Word | Target Color | Count (Target) | Ratio (vs Opp) | Ratio (vs Global) | Status |\n")
        f.write("|---|---|---|---|---|---|\n")
        
        for word, res in analysis_results.items():
            status = "VERIFIED" if res['verified'] else "NOT VERIFIED"
            ratio_opp_str = f"{res['ratio_opp']:.2f}x"
            ratio_glob_str = f"{res['ratio_global']:.2f}x"
            f.write(f"| `{word}` | {res['color']} | {res['count_target']} | {ratio_opp_str} | {ratio_glob_str} | **{status}** |\n")
            
        f.write("\n## Conclusion\n")
        verified_words = [w for w, r in analysis_results.items() if r['verified']]
        if verified_words:
            f.write(f"The following words have been verified and updated in the dictionary: {', '.join(verified_words)}.\n")
            for w in verified_words:
                f.write(f"- **{w}**: {'; '.join(analysis_results[w]['reasons'])}\n")
        else:
            f.write("No words were validated.\n")

def main():
    print("Parsing EVA data...")
    page_counts = parse_eva_data(EVA_FILE)
    if not page_counts:
        return

    print("Analyzing correlations...")
    analysis = analyze_correlations(page_counts)
    
    print("Generating report...")
    generate_report(analysis)
    
    print("Updating dictionary...")
    update_dictionary(analysis)
    
    print("Done.")

if __name__ == "__main__":
    main()
