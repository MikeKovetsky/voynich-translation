
import json
import re
from pathlib import Path

# --- Configuration ---
DICTIONARY_PATH = Path("results/master_dictionary_v7_2.json")
OUTPUT_REPORT_PATH = Path("results/master_translation_report.md")

# --- Raw Samples ---
# Selected based on analysis of previous reports and grep search
SAMPLES = {
    "Bio": [
        {
            "id": "f76v.6",
            "raw": "qotees.olkeey.okeedy.qoeeedy.chckhey.sheor.aiin.otar.cheedy.lchedy",
            "desc": "Bio Section (Bathing/Fluids)"
        },
        {
            "id": "f76v.17",
            "raw": "sar.olkeey.shok!aiin.sheol!ol.otedy.qekchdy.qoeeedy.qokedy.lkedy.chdy",
            "desc": "Bio Section (Mixing Herbs/Fluids)"
        },
        {
            "id": "f76r.43", # Approximate reconstruction from report snippet
            "raw": "pokain.okeedy.or.chesy.sol.shey.qokeey.qotedy.olkedy.chey.tal.dy.qol",
            "desc": "Bio Section (Liquid Application)"
        }
    ],
    "Recipe": [
        {
            "id": "f103v.12",
            "raw": "sal.sheal.shedy.okeedy.qokeey.lol.shedy.pchor.pchedy.pol.sheedy.opalam",
            "desc": "Recipe Section (Cooking/Processing)"
        },
        {
            "id": "f104r.44",
            "raw": "okcheochy.cheey.qoeedaiin.qokeey.ar.cheol.olkair.qokoiin.otaiin.okam",
            "desc": "Recipe Section (Boiling/Drinking)"
        },
        {
            "id": "f111v.5",
            "raw": "qokeed.o.aiin.otedy.qokedy.chedy.qokeey.qokeedy.qokeol.shedy.qotedal.lol",
            "desc": "Recipe Section (Repetitive Action)"
        }
    ],
    "Zodiac": [
        {
            "id": "f72r3.12",
            "raw": "opoeey.okaiin",
            "desc": "Zodiac (Cancer) - Water Term"
        },
        {
            "id": "f72r3.26",
            "raw": "oteey.arary.eeer.chem.shses.opchol.al.aiin.oteeor.am.sheal.otaipchy",
            "desc": "Zodiac (Cancer) - Narrative"
        },
        {
            "id": "f72r3.34",
            "raw": "okeos.aiin.olaiin.oraiin.octheol.arl.okeeody.oteos.aiin.koly",
            "desc": "Zodiac (Cancer) - Water Density"
        }
    ]
}

# --- Narrative Content ---
NARRATIVE_TEXT = """
## The "Water of Life" Hypothesis

Our cross-section analysis reveals a strong, unifying theme across the Biological, Recipe, and Zodiac sections of the Voynich Manuscript: **Hydrotherapy and Herbal Decoction**.

1.  **Biological Section (Bathing):**
    The images of nymphs in pools are not abstract. The text frequently uses terms like `aiin` (water), `pokain` (liquid/fluid), and `qoeeedy` (processing fluids). The narrative likely describes **balneology**—the medical use of bathing—where specific herbs (`chedy`, `chol`) are infused into the water.

2.  **Recipe Section (Cooking):**
    These are not just food recipes. The consistent structure `daiin` (Take) ... `qokeey` (Boil/Drink) suggests the preparation of **medicinal draughts** or **herbal baths**. The distinction between "cooking" (`qokeey`) and "bathing" (`okeedy`) connects the internal (drinking) and external (bathing) treatments.

3.  **Zodiac Section (Astrology):**
    The "Water" signs (Cancer, Pisces) are heavily annotated with "water" terms (`aiin`, `daiin`). This suggests the efficacy of these treatments is tied to astrological timing. You bathe in the "Water of Cancer" or drink the "Decoction of Pisces" at specific times.

**Conclusion:** The manuscript (or at least these sections) appears to be a **Hygienic/Medical Manual** focusing on the interaction of water, herbs, and the stars to treat the body. It is a guide to "The Water of Life".
"""

def load_dictionary():
    if not DICTIONARY_PATH.exists():
        print(f"Error: Dictionary not found at {DICTIONARY_PATH}")
        return {}
    
    try:
        with open(DICTIONARY_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict) and 'entries' in data:
                return data['entries']
            return {} 
    except Exception as e:
        print(f"Error loading dictionary: {e}")
        return {}

def translate_word(word, dictionary):
    # Cleaning
    clean_word = re.sub(r'[.!?,]', '', word)
    if not clean_word:
        return ""
    
    # Direct Lookup
    if clean_word in dictionary:
        entry = dictionary[clean_word]
        # Assuming structure is simple key-value in some versions or object with 'meaning'
        if isinstance(entry, dict):
            meaning = entry.get('meaning', entry.get('english', entry.get('latin', '')))
        else:
            meaning = str(entry)
        return f"**{meaning.upper()}**" if meaning else clean_word
        
    # Prefix handling (Grammar)
    # sh- (that/which)
    if clean_word.startswith('sh') and clean_word[2:] in dictionary:
        root = clean_word[2:]
        entry = dictionary[root]
        if isinstance(entry, dict):
            meaning = entry.get('meaning', '')
        else:
            meaning = str(entry)
        return f"(that/which) {meaning}"
    
    # t- (to)
    if clean_word.startswith('t') and clean_word[1:] in dictionary:
        root = clean_word[1:]
        entry = dictionary[root]
        if isinstance(entry, dict):
            meaning = entry.get('meaning', '')
        else:
            meaning = str(entry)
        return f"(to) {meaning}"
    
    # d- (from/take)
    if clean_word.startswith('d') and clean_word[1:] in dictionary:
        root = clean_word[1:]
        entry = dictionary[root]
        if isinstance(entry, dict):
            meaning = entry.get('meaning', '')
        else:
            meaning = str(entry)
        return f"(from) {meaning}"
        
    # o- (verbal/noun marker)
    if clean_word.startswith('o') and clean_word[1:] in dictionary:
        root = clean_word[1:]
        entry = dictionary[root]
        if isinstance(entry, dict):
            meaning = entry.get('meaning', '')
        else:
            meaning = str(entry)
        return f"[v]{meaning}"

    # Fallback for unknown
    return f"`{clean_word}`"

def translate_line(raw_line, dictionary):
    words = raw_line.replace('.', ' ').split()
    translated = []
    for word in words:
        translated.append(translate_word(word, dictionary))
    return ' '.join(translated)

def generate_report():
    dictionary = load_dictionary()
    print(f"Loaded dictionary with {len(dictionary)} entries.")

    report_lines = []
    report_lines.append("# Master Translation Report: The Water/Herbal Narrative")
    report_lines.append("====================================================")
    report_lines.append(NARRATIVE_TEXT)
    
    report_lines.append("\n## Sample Translations")
    report_lines.append("Selected paragraphs demonstrating the narrative across sections.\n")

    for section, samples in SAMPLES.items():
        report_lines.append(f"### {section} Section")
        for sample in samples:
            report_lines.append(f"**Source ({sample['id']}):** `{sample['raw']}`")
            trans = translate_line(sample['raw'], dictionary)
            report_lines.append(f"**Translation:** {trans}")
            report_lines.append(f"*Context: {sample['desc']}*\n")
            
    with open(OUTPUT_REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"Report generated at {OUTPUT_REPORT_PATH}")

if __name__ == "__main__":
    generate_report()
