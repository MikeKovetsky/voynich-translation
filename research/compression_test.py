import zlib
import lzma
import random
import os
from research.voynich_data import get_all_words, get_eva_pages

OUTPUT_FILE = "results/compression_stats.md"
LATIN_FILE = "data/external_corpora/latin_medical.txt"

def calculate_bits_per_char(text, compressed_data):
    if not text: return 0
    # Bits = bytes * 8
    return (len(compressed_data) * 8) / len(text)

def main():
    results = []
    
    # 1. Load Voynich Text
    print("Loading Voynich...")
    pages = get_eva_pages()
    voynich_text = ""
    for folio in pages.values():
        voynich_text += " ".join(folio.values()) + " "
    
    voynich_text = voynich_text.strip()
    
    # 2. Load Latin Control
    print("Loading Latin...")
    if os.path.exists(LATIN_FILE):
        with open(LATIN_FILE, 'r', encoding='utf-8') as f:
            latin_words = f.read().split()
            # Simulate text length match
            latin_text = " ".join(latin_words)
            # Repeat to match length if needed
            if len(latin_text) < len(voynich_text):
                factor = int(len(voynich_text) / len(latin_text)) + 1
                latin_text = (latin_text + " ") * factor
            latin_text = latin_text[:len(voynich_text)]
    else:
        latin_text = "Latin corpus missing."

    # 3. Create Random Control (Scrambled Voynich)
    print("Generating Random Control...")
    v_chars = list(voynich_text)
    random.shuffle(v_chars)
    random_text = "".join(v_chars)
    
    # 4. Compression Tests
    datasets = {
        "Voynich (EVA)": voynich_text,
        "Latin (Medical)": latin_text,
        "Random Scramble": random_text,
        "English (Sample)": "The quick brown fox jumps over the lazy dog. " * (len(voynich_text)//44) 
    }
    
    report = ["# Compression Analysis (Information Density)\n"]
    report.append("| Dataset | Original Size | Zlib Size | LZMA Size | Zlib BPC | LZMA BPC | Ratio (Zlib) |")
    report.append("|---|---|---|---|---|---|---|")
    
    for name, text in datasets.items():
        if not text or text == "Latin corpus missing.":
            continue
            
        encoded = text.encode('utf-8')
        zlib_comp = zlib.compress(encoded)
        lzma_comp = lzma.compress(encoded)
        
        z_bpc = calculate_bits_per_char(text, zlib_comp)
        l_bpc = calculate_bits_per_char(text, lzma_comp)
        ratio = len(text) / len(zlib_comp)
        
        report.append(f"| {name} | {len(text)} | {len(zlib_comp)} | {len(lzma_comp)} | {z_bpc:.2f} | {l_bpc:.2f} | {ratio:.2f} |")

    # 5. Entropy Calculation (0-order)
    report.append("\n## Character Entropy (0-order)\n")
    for name, text in datasets.items():
        if not text or text == "Latin corpus missing.": continue
        counts = Counter(text)
        total = len(text)
        entropy = 0
        for count in counts.values():
            p = count / total
            entropy -= p * math.log2(p)
        report.append(f"- **{name}:** {entropy:.4f} bits/char")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
        
    print(f"Analysis complete. See {OUTPUT_FILE}")

import math
from collections import Counter

if __name__ == "__main__":
    main()
