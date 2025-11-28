import json
import itertools
from difflib import SequenceMatcher
import os

# Configuration
INPUT_JSON = 'results/astronomical_candidates.json'
OUTPUT_MATCHES = 'results/astro_matches.md'
OUTPUT_SUMMARY = 'results/track-308-results_summary.md'

# Mappings
EVA_TO_PHONETIC = {
    'o': ['a', 'o', 'w'],
    'k': ['k', 'q', 'g'],
    '8': ['d', 't', 's'],
    '9': ['y', 'i', 'm', 'n'],
    'c': ['e', 'k', 'ch'],
    'h': ['h', 'e', 'ii'],
    '1': ['i', 'l', 'r'],
    '2': ['k', 't'],
    '4': ['q', 'p', 'd'],
    '7': ['l', 'r'],
    'a': ['a'],
    'e': ['e'],
    'i': ['i', 'y'],
    'n': ['n'],
    'm': ['m'],
    's': ['s', 'sh'],
    't': ['t'],
    'y': ['y', 'i'],
    'l': ['l'],
    'r': ['r'],
    'd': ['d'],
    'S': ['s', 'sh'],
    'N': ['n', 'm'],
    'M': ['m'],
    'H': ['h', 'k'],
    'C': ['e', 'k'],
    'p': ['p', 'f'],
    'f': ['f', 'p'],
    '$': ['s', 'sh'], # special character
}

HEBREW_MONTHS = ["Nisan", "Iyar", "Sivan", "Tammuz", "Av", "Elul", "Tishrei", "Cheshvan", "Kislev", "Tevet", "Shevat", "Adar"]
LATIN_MONTHS = ["Januarius", "Februarius", "Martius", "Aprilis", "Maius", "Iunius", "Iulius", "Augustus", "September", "October", "November", "December"]
# Common Arabic Star Names (expanded list)
ARABIC_STARS = [
    "Aldebaran", "Altair", "Rigel", "Betelgeuse", "Deneb", "Vega", "Capella", "Arcturus", "Antares", "Spica", 
    "Pollux", "Fomalhaut", "Denebola", "Regulus", "Castor", "Achernar", "Hadar", "Acrux", "Alioth", "Mirfak", 
    "Dubhe", "Wezen", "Sargas", "Menkar", "Alpheratz", "Hamal", "Diphda", "Alnitak", "Saiph", "Algol", "Rasalhague",
    "Almach", "Alphard", "Algenib", "Markab", "Enif", "Scheat", "Mizar", "Merak", "Phad", "Megrez", "Alioth", "Alkaid"
]

def get_phonetic_variants(word):
    """Generates all phonetic variants for a given EVA word."""
    options = []
    for char in word:
        if char in EVA_TO_PHONETIC:
            options.append(EVA_TO_PHONETIC[char])
        else:
            options.append([char]) # Keep original if no mapping
    
    # Cartesian product
    variants = [''.join(p) for p in itertools.product(*options)]
    # Limit to avoid explosion if word is long (though EVA words are usually short)
    if len(variants) > 1000:
        return variants[:1000]
    return variants

def fuzzy_score(s1, s2):
    """Returns a similarity score between 0 and 1."""
    return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()

def validate_candidates():
    if not os.path.exists(INPUT_JSON):
        print(f"Input file {INPUT_JSON} not found.")
        return

    with open(INPUT_JSON, 'r') as f:
        data = json.load(f)
    
    labels = data.get('labels', [])
    results = []

    print(f"Processing {len(labels)} labels...")

    for label_entry in labels:
        location = label_entry.get('location', 'Unknown')
        words = label_entry.get('words', [])
        
        for word in words:
            variants = get_phonetic_variants(word)
            
            best_match = None
            best_score = 0
            match_type = ""
            match_target = ""
            match_variant = ""

            # Check Hebrew
            for target in HEBREW_MONTHS:
                for variant in variants:
                    score = fuzzy_score(variant, target)
                    if score > best_score:
                        best_score = score
                        match_type = "Hebrew Month"
                        match_target = target
                        match_variant = variant

            # Check Latin
            for target in LATIN_MONTHS:
                for variant in variants:
                    score = fuzzy_score(variant, target)
                    if score > best_score:
                        best_score = score
                        match_type = "Latin Month"
                        match_target = target
                        match_variant = variant
            
            # Check Arabic Stars
            for target in ARABIC_STARS:
                for variant in variants:
                    score = fuzzy_score(variant, target)
                    if score > best_score:
                        best_score = score
                        match_type = "Arabic Star"
                        match_target = target
                        match_variant = variant
            
            if best_score > 0.6: # Threshold
                results.append({
                    "location": location,
                    "voynich_word": word,
                    "variant": match_variant,
                    "match_type": match_type,
                    "match_target": match_target,
                    "score": round(best_score, 3)
                })

    # Sort by score descending
    results.sort(key=lambda x: x['score'], reverse=True)

    # Write detailed matches
    print(f"Writing {len(results)} matches to {OUTPUT_MATCHES}...")
    with open(OUTPUT_MATCHES, 'w') as f:
        f.write("# Astronomical Label Matches (Track 308)\n\n")
        f.write("| Location | Voynich Word | Phonetic Variant | Match Target | Type | Score |\n")
        f.write("|---|---|---|---|---|---|\n")
        for r in results:
            f.write(f"| {r['location']} | {r['voynich_word']} | {r['variant']} | {r['match_target']} | {r['match_type']} | {r['score']} |\n")

    # Write Summary
    print(f"Writing summary to {OUTPUT_SUMMARY}...")
    with open(OUTPUT_SUMMARY, 'w') as f:
        f.write("# Track 308: Astronomical Label Validation Results\n\n")
        f.write("## Summary\n")
        f.write(f"Processed {len(labels)} label candidates.\n")
        f.write(f"Found {len(results)} potential matches with confidence > 0.6.\n\n")
        
        # Top matches
        f.write("## Top Matches (Score >= 0.75)\n")
        f.write("| Location | Voynich Word | Target | Type | Score |\n")
        f.write("|---|---|---|---|---|\n")
        top_matches = [r for r in results if r['score'] >= 0.75]
        for r in top_matches:
             f.write(f"| {r['location']} | {r['voynich_word']} | {r['match_target']} | {r['match_type']} | {r['score']} |\n")
        
        if not top_matches:
            f.write("No matches with score >= 0.75 found.\n")

        f.write("\n## Conclusion\n")
        if len(top_matches) > 3:
             f.write("Several strong candidates identified. Arabic Star names seem to be the most frequent matches. Further linguistic analysis required.\n")
        else:
             f.write("Few strong matches found. The phonetic mapping might need refinement or the labels are not simple month/star names.\n")

if __name__ == "__main__":
    validate_candidates()
