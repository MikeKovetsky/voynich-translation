import json
import os
import re

def get_section(page):
    # Extract number
    match = re.match(r'f(\d+)([rv]?)', page)
    if not match:
        return "Unknown"
    
    try:
        num = int(match.group(1))
    except:
        return "Unknown"
    
    if 1 <= num <= 66:
        return "Botanical"
    elif 67 <= num <= 73:
        return "Astronomical"
    elif 75 <= num <= 84:
        return "Biological"
    elif 85 <= num <= 86:
        return "Cosmological"
    elif 87 <= num <= 102:
        return "Pharmaceutical"
    elif 103 <= num <= 116:
        return "Recipes"
    else:
        return "Unknown"

def calculate_confidence(text):
    # Simple heuristic: 
    # - Punishment for '?' (unknowns)
    # - Punishment for untranslated words (maybe check for non-English chars if possible, but simpler to just check for '?')
    # - Reward for length?
    
    if not text or text.strip() == "":
        return 0
        
    # Remove markdown headers/bolding for analysis
    clean_text = re.sub(r'\*\*.*?\*\*', '', text)
    clean_text = re.sub(r'#.*', '', clean_text)
    
    words = clean_text.split()
    if not words:
        return 0
        
    question_marks = text.count('?')
    unknown_tags = text.count('UNKNOWN') + text.count('verb (unknown)')
    
    total_tokens = len(words)
    if total_tokens == 0: 
        return 0
        
    # Base confidence starts at 100
    # Deduct for uncertainty markers
    confidence = 100.0
    
    # If text is very short (e.g. just "f1r"), confidence is 0
    if len(text) < 50:
        return 0
        
    penalty = (question_marks + unknown_tags) * 2
    confidence -= (penalty / max(total_tokens, 1)) * 100
    
    # Cap at 0-100
    return max(0.0, min(100.0, confidence))

def main():
    print("Generating web statistics...")
    
    base_dir = "web/src/data"
    translations_path = os.path.join(base_dir, "translations.json")
    
    if not os.path.exists(translations_path):
        print("Error: translations.json not found")
        return

    with open(translations_path, 'r') as f:
        translations = json.load(f)
        
    stats = {
        "global": {
            "total_pages": 0,
            "translated_pages": 0,
            "coverage_percent": 0,
            "avg_confidence": 0
        },
        "sections": {}
    }
    
    # Initialize sections
    sections = ["Botanical", "Astronomical", "Biological", "Cosmological", "Pharmaceutical", "Recipes", "Unknown"]
    for sec in sections:
        stats["sections"][sec] = {
            "total_pages": 0, # We'll count observed pages
            "translated_pages": 0,
            "avg_confidence": 0,
            "confidence_sum": 0
        }

    # Known total pages per section (approximate for denominator if we wanted absolute coverage, 
    # but better to rely on the pages we actually have files for or just count what we see)
    # Let's rely on the keys in translations.json + pages.json if available
    
    pages_path = os.path.join(base_dir, "pages.json")
    all_pages = []
    if os.path.exists(pages_path):
        with open(pages_path, 'r') as f:
            all_pages = json.load(f)
            # Normalize: remove .jpg if present
            all_pages = [p.replace('.jpg', '') for p in all_pages]
    else:
        all_pages = list(translations.keys())

    # Count totals per section
    for page in all_pages:
        sec = get_section(page)
        if sec == "Unknown":
             pass # print(f"Warning: Page {page} classified as Unknown")
        if sec not in stats["sections"]:
            stats["sections"][sec] = {"total_pages": 0, "translated_pages": 0, "avg_confidence": 0, "confidence_sum": 0}
        stats["sections"][sec]["total_pages"] += 1

    stats["global"]["total_pages"] = len(all_pages)
    
    # Analyze translations
    total_confidence = 0
    translated_count = 0
    
    for page, text in translations.items():
        if page not in all_pages:
            # This page has a translation but wasn't in pages.json? Add it.
            sec = get_section(page)
            if sec not in stats["sections"]:
                stats["sections"][sec] = {"total_pages": 0, "translated_pages": 0, "avg_confidence": 0, "confidence_sum": 0}
            stats["sections"][sec]["total_pages"] += 1
            all_pages.append(page)
            stats["global"]["total_pages"] += 1
            
        sec = get_section(page)
        
        # Check if it's actually translated or just a placeholder
        if len(text) > 50 and "?" not in text[:10]: # Simple check
             translated_count += 1
             conf = calculate_confidence(text)
             
             stats["sections"][sec]["translated_pages"] += 1
             stats["sections"][sec]["confidence_sum"] += conf
             
             total_confidence += conf
    
    stats["global"]["translated_pages"] = translated_count
    if translated_count > 0:
        stats["global"]["avg_confidence"] = round(total_confidence / translated_count, 1)
        stats["global"]["coverage_percent"] = round((translated_count / stats["global"]["total_pages"]) * 100, 1)
    
    # Finalize section stats
    for sec in stats["sections"]:
        s = stats["sections"][sec]
        if s["translated_pages"] > 0:
            s["avg_confidence"] = round(s["confidence_sum"] / s["translated_pages"], 1)
            s["coverage_percent"] = round((s["translated_pages"] / s["total_pages"]) * 100, 1)
        else:
            s["avg_confidence"] = 0
            s["coverage_percent"] = 0
        del s["confidence_sum"] # Remove temp field

    # Write output
    output_path = os.path.join(base_dir, "stats.json")
    with open(output_path, 'w') as f:
        json.dump(stats, f, indent=2)
        
    print(f"Stats written to {output_path}")
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    main()
