import json
import re
from collections import defaultdict

PHONETIC_MAP = {
    "o": "a", "h": "r", "9": "s", "k": "n", "c": "c", "7": "l", "m": "m",
    "a": "e", "e": "i", "8": "d", "1": "t", "4": "qu", "y": "i", "2": "b",
    "C": "ch", "s": "x", "n": "n", "p": "p", "g": "g", "j": "i", "W": "u",
    "H": "h", "z": "z", "u": "u", "f": "f", "A": "a", "d": "v", "J": "i",
    "Z": "z", "K": "c", "i": "i", "S": "s", "t": "t", "b": "b", "E": "e",
    "M": "m", "Q": "q", "I": "i", "N": "n", "l": "l"
}

ABBREVIATIONS = {
    "-9": "-us/-is (nominative)",
    "-89": "-orum/-arum (genitive plural)",
    "-am": "-am (accusative)",
    "-oe": "-ae (dative/ablative)",
    "-ay": "-i (genitive)",
    "-an": "-um (accusative neuter)",
    "-ae": "-ae (genitive/dative fem.)",
    "-c9": "-cus/-cis (adjectival)"
}

LATIN_BOTANICAL = {
    "aqua": "water", "radix": "root", "flos": "flower", "herba": "herb",
    "folium": "leaf", "caulis": "stalk", "cortex": "bark", "semen": "seed",
    "succus": "juice", "oleum": "oil", "bacca": "berry", "ramus": "branch",
    "stirps": "stem", "fructus": "fruit", "ulcus": "ulcer/sore",
    "stomachus": "stomach", "manus": "hand", "auris": "ear", "oculus": "eye",
    "dens": "tooth", "caput": "head", "pectus": "chest"
}

LATIN_MEDICAL = {
    "febris": "fever", "dolor": "pain", "venenum": "poison", "tumor": "swelling",
    "morbus": "disease", "quartana": "quartan fever"
}

LATIN_PREPOSITIONS = {
    "de": "of/from", "ad": "to/for", "in": "in", "cum": "with",
    "contra": "against", "pro": "for", "per": "through"
}

LATIN_VERBS = {
    "valet": "is effective", "curat": "cures", "sanat": "heals",
    "prodest": "helps", "tollit": "removes", "solvit": "dissolves",
    "facit": "makes", "habet": "has", "est": "is"
}

LATIN_ADJECTIVES = {
    "calidus": "warm/hot", "frigidus": "cold", "siccus": "dry",
    "humidus": "wet", "albus": "white", "niger": "black",
    "magnus": "large", "parvus": "small", "bonus": "good"
}

def decode_voynich(word):
    result = []
    i = 0
    while i < len(word):
        if word[i] in PHONETIC_MAP:
            result.append(PHONETIC_MAP[word[i]])
        else:
            result.append(word[i])
        i += 1
    return "".join(result)

def sim_score(s1, s2):
    if not s1 or not s2:
        return 0
    s1, s2 = s1.lower(), s2.lower()
    matches = sum(1 for a, b in zip(s1, s2) if a == b)
    return (2.0 * matches) / (len(s1) + len(s2))

def categorize(decoded, latin, english):
    if latin in LATIN_PREPOSITIONS or english in LATIN_PREPOSITIONS.values():
        return "preposition"
    if latin in LATIN_VERBS or english in LATIN_VERBS.values():
        return "verb"
    if latin in LATIN_BOTANICAL or english in LATIN_BOTANICAL.values():
        return "noun_botanical"
    if latin in LATIN_MEDICAL or english in LATIN_MEDICAL.values():
        return "noun_medical"
    if latin in LATIN_ADJECTIVES or english in LATIN_ADJECTIVES.values():
        return "adjective"
    if decoded.endswith("s") or decoded.endswith("m"):
        return "noun"
    return "unknown"

def load_claston():
    words = defaultdict(int)
    try:
        with open("voynich_transcription.txt") as f:
            for line in f:
                if line.startswith("<"):
                    continue
                for word in re.findall(r"[a-zA-Z0-9]+", line):
                    words[word] += 1
    except:
        pass
    return words

def collect_all_mappings():
    entries = {}
    word_counts = load_claston()
    
    # === SOURCE 0: Botanical Word Frequency (biggest source) ===
    try:
        with open("results/botanical_word_frequency.json") as f:
            data = json.load(f)
        
        for item in data.get("top_500_words", []):
            decoded = item.get("decoded", "")
            if not decoded or decoded.startswith("-") or len(decoded) < 2:
                continue
            
            # Try to find the Voynich form
            voynich = None
            for w in word_counts:
                if decode_voynich(w) == decoded.replace("-", ""):
                    voynich = w
                    break
            
            if not voynich:
                # Reverse-engineer voynich from decoded
                rev_map = {v: k for k, v in PHONETIC_MAP.items() if len(k) == 1}
                voynich = ""
                for ch in decoded.replace("-", ""):
                    voynich += rev_map.get(ch, ch)
            
            latin = item.get("latin_match", "")
            score = item.get("score", 0.45)
            match_type = item.get("type", "phonetic")
            
            conf = score * 0.9 if match_type in ["exact", "stem"] else score * 0.7
            
            if voynich and voynich not in entries:
                english = LATIN_BOTANICAL.get(latin, LATIN_MEDICAL.get(latin, LATIN_PREPOSITIONS.get(latin, latin)))
                entries[voynich] = {
                    "voynich": voynich,
                    "decoded": decoded.replace("-", ""),
                    "latin": latin,
                    "english": english,
                    "confidence": round(conf, 3),
                    "category": categorize(decoded, latin, english),
                    "occurrences": item.get("count", 0),
                    "source": "botanical_word_frequency.json"
                }
    except Exception as e:
        print(f"Error loading botanical_word_frequency.json: {e}")
    
    # === SOURCE 0.5: Voynich Vocabulary ===
    try:
        with open("results/voynich_vocabulary.json") as f:
            data = json.load(f)
        
        for item in data.get("vocabulary", []):
            v = item.get("voynich", "")
            if not v:
                continue
            
            decoded = item.get("decoded", decode_voynich(v))
            latin_match = item.get("latin_match", "")
            # Extract just the Latin word from "word (meaning)" format
            latin = latin_match.split()[0] if latin_match else ""
            english = latin_match.split("(")[1].rstrip(")") if "(" in latin_match else latin
            
            conf = item.get("confidence", 0.5)
            cat = item.get("category", "unknown").lower()
            if cat == "possible":
                cat = "unknown"
            
            # Only add if not already present or higher confidence
            if v not in entries or entries[v]["confidence"] < conf:
                entries[v] = {
                    "voynich": v,
                    "decoded": decoded,
                    "latin": latin,
                    "english": english,
                    "confidence": round(conf, 3),
                    "category": cat if cat in ["preposition", "botanical", "medical", "disease", "property", "number", "action", "zodiac"] else categorize(decoded, latin, english),
                    "occurrences": item.get("count", 0),
                    "source": "voynich_vocabulary.json"
                }
            
            # Also add related forms with slightly lower confidence
            for related in item.get("related_forms", [])[:3]:
                if related not in entries:
                    entries[related] = {
                        "voynich": related,
                        "decoded": decode_voynich(related),
                        "latin": latin,
                        "english": f"variant of {v}",
                        "confidence": round(conf * 0.8, 3),
                        "category": entries[v]["category"],
                        "occurrences": word_counts.get(related, 0),
                        "source": "voynich_vocabulary.json"
                    }
    except Exception as e:
        print(f"Error loading voynich_vocabulary.json: {e}")
    
    # === SOURCE 1: Anchor Word Validation ===
    try:
        with open("results/anchor_word_validation.json") as f:
            data = json.load(f)
        
        # Paradigm words (highest confidence)
        if "anchor_words" in data:
            for aw in data["anchor_words"]:
                if aw.get("validation_status") == "CONFIRMED" and "paradigm_forms" in aw:
                    for form, count in aw["paradigm_forms"].items():
                        decoded = decode_voynich(form)
                        case = "ablative" if form.endswith("an") else \
                               "accusative" if form.endswith("am") else \
                               "instrumental" if form.endswith("ae") else \
                               "genitive" if form.endswith("ay") else \
                               "locative" if form.endswith("oe") else \
                               "gen.plural" if form.endswith("89") else "nominative"
                        entries[form] = {
                            "voynich": form,
                            "decoded": decoded,
                            "latin": "herba",
                            "english": f"the herb ({case})",
                            "confidence": 0.9,
                            "category": "noun_botanical",
                            "occurrences": count,
                            "source": "anchor_word_validation.json"
                        }
        
        # Validated vocabulary
        for voc in data.get("validated_vocabulary", []):
            v = voc["voynich"]
            if v not in entries:
                entries[v] = {
                    "voynich": v,
                    "decoded": decode_voynich(v),
                    "latin": voc.get("meaning", "").split()[0].lower() if voc.get("meaning") else "",
                    "english": voc.get("meaning", ""),
                    "confidence": voc.get("confidence", 0.5),
                    "category": categorize(decode_voynich(v), "", voc.get("meaning", "")),
                    "occurrences": word_counts.get(v, 0),
                    "source": "anchor_word_validation.json"
                }
    except Exception as e:
        print(f"Error loading anchor_word_validation.json: {e}")
    
    # === SOURCE 2: Common Words Decoded ===
    try:
        with open("results/common_words_decoded.json") as f:
            data = json.load(f)
        
        for dm in data.get("decoded_meanings", []):
            v = dm["voynich"]
            conf = dm.get("confidence", 0.5)
            if v not in entries or entries[v]["confidence"] < conf:
                entries[v] = {
                    "voynich": v,
                    "decoded": dm.get("decoded", decode_voynich(v)),
                    "latin": dm.get("proposed", ""),
                    "english": dm.get("meaning", ""),
                    "confidence": conf,
                    "category": categorize(dm.get("decoded", ""), dm.get("proposed", ""), dm.get("meaning", "")),
                    "occurrences": word_counts.get(v, 0),
                    "source": "common_words_decoded.json"
                }
        
        for para_name, para in data.get("paradigms", {}).items():
            for form in para.get("forms", []):
                v = form["voynich"]
                if v not in entries:
                    entries[v] = {
                        "voynich": v,
                        "decoded": form.get("decoded", decode_voynich(v)),
                        "latin": para.get("best_hypothesis", "").split()[0] if para.get("best_hypothesis") else "",
                        "english": para.get("best_hypothesis", ""),
                        "confidence": para.get("confidence", 0.5),
                        "category": "paradigm",
                        "occurrences": form.get("count", 0),
                        "source": "common_words_decoded.json"
                    }
        
        # Add function words
        for fw in data.get("function_words", []):
            v = fw.get("voynich", "")
            if v and v not in entries:
                match = fw.get("best_latin_match", {})
                entries[v] = {
                    "voynich": v,
                    "decoded": fw.get("decoded", decode_voynich(v)),
                    "latin": match.get("latin", ""),
                    "english": match.get("meaning", ""),
                    "confidence": match.get("similarity", 0.5),
                    "category": categorize(fw.get("decoded", ""), match.get("latin", ""), match.get("meaning", "")),
                    "occurrences": fw.get("count", 0),
                    "source": "common_words_decoded.json"
                }
        
        # Add short words
        for sw in data.get("short_words", []):
            v = sw.get("voynich", "")
            if v and v not in entries:
                entries[v] = {
                    "voynich": v,
                    "decoded": sw.get("decoded", decode_voynich(v)),
                    "latin": sw.get("hypothesis", "").split()[0] if sw.get("hypothesis") else "",
                    "english": sw.get("hypothesis", ""),
                    "confidence": 0.6 if sw.get("is_likely_suffix") else 0.4,
                    "category": "suffix" if sw.get("is_likely_suffix") else "unknown",
                    "occurrences": sw.get("count", 0),
                    "source": "common_words_decoded.json"
                }
    except Exception as e:
        print(f"Error loading common_words_decoded.json: {e}")
    
    # === SOURCE 3: Zodiac Latin Analysis ===
    try:
        with open("results/zodiac_latin_analysis.json") as f:
            data = json.load(f)
        
        for match in data.get("zodiac_sign_matches", []):
            v = match["voynich"]
            if match.get("status") in ["CONFIRMED", "LIKELY"]:
                conf = 0.85 if match["status"] == "CONFIRMED" else 0.7
                if v not in entries or entries[v]["confidence"] < conf:
                    entries[v] = {
                        "voynich": v,
                        "decoded": match.get("decoded", decode_voynich(v)),
                        "latin": match.get("target", ""),
                        "english": f"{match.get('sign', '')} (zodiac sign)",
                        "confidence": conf,
                        "category": "zodiac",
                        "occurrences": word_counts.get(v, 0),
                        "source": "zodiac_latin_analysis.json"
                    }
        
        for match in data.get("star_matches", []):
            v = match["voynich"]
            if match.get("score", 0) >= 0.5:
                conf = min(0.8, match["score"])
                if v not in entries or entries[v]["confidence"] < conf:
                    entries[v] = {
                        "voynich": v,
                        "decoded": match.get("decoded", decode_voynich(v)),
                        "latin": match.get("star", "").lower(),
                        "english": f"{match.get('star', '')} (star in {match.get('sign', '')})",
                        "confidence": conf,
                        "category": "star",
                        "occurrences": word_counts.get(v, 0),
                        "source": "zodiac_latin_analysis.json"
                    }
        
        # Add zodiac vocabulary
        for sign, words in data.get("complete_vocabulary", {}).items():
            for word_obj in words[:10]:  # Top 10 per sign
                v = word_obj.get("voynich", "")
                decoded = word_obj.get("decoded", "")
                if v and decoded and v not in entries:
                    entries[v] = {
                        "voynich": v,
                        "decoded": decoded,
                        "latin": "",
                        "english": f"zodiac term ({sign})",
                        "confidence": 0.4,
                        "category": "zodiac_vocab",
                        "occurrences": word_counts.get(v, 0),
                        "source": "zodiac_latin_analysis.json"
                    }
    except Exception as e:
        print(f"Error loading zodiac_latin_analysis.json: {e}")
    
    # === SOURCE 4: Latin Verbs ===
    try:
        with open("results/latin_verbs.json") as f:
            data = json.load(f)
        
        for verb in data.get("target_verbs", []):
            if verb.get("best_match") and verb.get("confidence", 0) >= 0.5:
                v = verb["best_match"]
                cands = [c for c in verb.get("candidates", []) if c["voynich"] == v]
                decoded = cands[0].get("decoded", decode_voynich(v)) if cands else decode_voynich(v)
                
                if v not in entries or entries[v]["confidence"] < verb["confidence"]:
                    entries[v] = {
                        "voynich": v,
                        "decoded": decoded,
                        "latin": verb["latin"],
                        "english": verb.get("meaning", ""),
                        "confidence": verb["confidence"],
                        "category": "verb",
                        "occurrences": word_counts.get(v, 0),
                        "source": "latin_verbs.json"
                    }
    except Exception as e:
        print(f"Error loading latin_verbs.json: {e}")
    
    # === SOURCE 5: Phrase Patterns ===
    try:
        with open("results/phrase_patterns.json") as f:
            data = json.load(f)
        
        for de_pat in data.get("de_patterns", {}).get("sequences_found", [])[:20]:
            words = de_pat["voynich"].split()
            if len(words) >= 2 and words[0].startswith("8a"):
                v = words[0]
                if v not in entries:
                    entries[v] = {
                        "voynich": v,
                        "decoded": decode_voynich(v),
                        "latin": "de",
                        "english": "of/from",
                        "confidence": 0.8,
                        "category": "preposition",
                        "occurrences": word_counts.get(v, 0),
                        "source": "phrase_patterns.json"
                    }
        
        # Add herb patterns (4oh- prefix)
        for herb_pat in data.get("herb_patterns", [])[:50]:
            v = herb_pat.get("word", "")
            if v and v not in entries:
                entries[v] = {
                    "voynich": v,
                    "decoded": herb_pat.get("decoded", decode_voynich(v)),
                    "latin": "herba",
                    "english": "herb/plant term",
                    "confidence": 0.6,
                    "category": "noun_botanical",
                    "occurrences": word_counts.get(v, 0),
                    "source": "phrase_patterns.json"
                }
        
        # Add top bigrams as phrase entries
        for bigram in data.get("top_bigrams", [])[:30]:
            v = bigram.get("voynich", "").replace(" ", "_")
            if v and "_" in v and v not in entries:
                entries[v] = {
                    "voynich": v,
                    "decoded": bigram.get("decoded", ""),
                    "latin": bigram.get("latin_match", "") or "",
                    "english": f"phrase ({bigram.get('count', 0)}x)",
                    "confidence": 0.5,
                    "category": "phrase",
                    "occurrences": bigram.get("count", 0),
                    "source": "phrase_patterns.json"
                }
    except Exception as e:
        print(f"Error loading phrase_patterns.json: {e}")
    
    # === Add Perfect Matches ===
    perfect_matches = [
        ("o4o", "aqua", "aqua", "water", 1.0, "noun_botanical"),
        ("8am", "dem", "de", "of/from", 0.85, "preposition"),
        ("oh9", "ars", "aries", "Aries (zodiac)", 0.85, "zodiac"),
        ("7am", "lem", "leo", "Leo (zodiac)", 0.75, "zodiac"),
        ("okco", "anca", "cancer", "Cancer (zodiac)", 0.65, "zodiac"),
    ]
    
    for v, dec, lat, eng, conf, cat in perfect_matches:
        if v not in entries or entries[v]["confidence"] < conf:
            entries[v] = {
                "voynich": v,
                "decoded": dec,
                "latin": lat,
                "english": eng,
                "confidence": conf,
                "category": cat,
                "occurrences": word_counts.get(v, 0),
                "source": "confirmed_matches"
            }
    
    # === Add Common Suffixes/Endings ===
    suffixes = [
        ("9", "s", "-us/-is", "nominative marker", 0.85, "suffix"),
        ("89", "ds", "-orum/-arum", "genitive plural", 0.8, "suffix"),
        ("am", "em", "-am", "accusative", 0.75, "suffix"),
        ("oe", "ai", "-ae", "dative/locative", 0.7, "suffix"),
        ("ay", "ei", "-i", "genitive", 0.7, "suffix"),
        ("an", "en", "-um", "accusative neuter", 0.65, "suffix"),
    ]
    
    for v, dec, lat, eng, conf, cat in suffixes:
        if v not in entries:
            entries[v] = {
                "voynich": v,
                "decoded": dec,
                "latin": lat,
                "english": eng,
                "confidence": conf,
                "category": cat,
                "occurrences": word_counts.get(v, 0),
                "source": "grammar_analysis"
            }
    
    return entries

def lookup(voynich_word, dictionary):
    if voynich_word in dictionary:
        e = dictionary[voynich_word]
        return {"latin": e["latin"], "english": e["english"], "confidence": e["confidence"]}
    return None

def reverse_lookup(latin_word, dictionary):
    results = []
    for v, e in dictionary.items():
        lat = e.get("latin", "")
        if lat and lat.lower() == latin_word.lower():
            results.append({"voynich": v, "confidence": e["confidence"]})
    return sorted(results, key=lambda x: -x["confidence"])

def get_by_category(category, dictionary):
    return [e for e in dictionary.values() if e["category"] == category]

def get_by_confidence(min_conf, dictionary):
    return [e for e in dictionary.values() if e["confidence"] >= min_conf]

def main():
    print("Building Master Dictionary...")
    entries = collect_all_mappings()
    
    entries_list = sorted(entries.values(), key=lambda x: (-x["confidence"], -x["occurrences"]))
    
    by_category = defaultdict(list)
    for e in entries_list:
        by_category[e["category"]].append(e["voynich"])
    
    high_conf = [e for e in entries_list if e["confidence"] >= 0.8]
    
    master_dict = {
        "version": "1.0",
        "total_entries": len(entries_list),
        "entries": entries_list,
        "by_category": dict(by_category),
        "phonetic_key": PHONETIC_MAP,
        "abbreviations": ABBREVIATIONS,
        "statistics": {
            "total": len(entries_list),
            "high_confidence": len([e for e in entries_list if e["confidence"] >= 0.8]),
            "medium_confidence": len([e for e in entries_list if 0.5 <= e["confidence"] < 0.8]),
            "low_confidence": len([e for e in entries_list if e["confidence"] < 0.5]),
            "by_category": {k: len(v) for k, v in by_category.items()}
        }
    }
    
    with open("results/master_dictionary.json", "w") as f:
        json.dump(master_dict, f, indent=2)
    print(f"Saved master_dictionary.json with {len(entries_list)} entries")
    
    with open("results/high_confidence_words.json", "w") as f:
        json.dump({"entries": high_conf, "count": len(high_conf)}, f, indent=2)
    print(f"Saved high_confidence_words.json with {len(high_conf)} entries")
    
    # Generate report
    report = f"""# Master Dictionary Report

## Overview

| Metric | Value |
|--------|-------|
| **Total Entries** | {len(entries_list)} |
| **High Confidence (≥0.8)** | {master_dict['statistics']['high_confidence']} |
| **Medium Confidence (0.5-0.8)** | {master_dict['statistics']['medium_confidence']} |
| **Low Confidence (<0.5)** | {master_dict['statistics']['low_confidence']} |

## Entries by Category

| Category | Count |
|----------|-------|
"""
    for cat, count in sorted(master_dict["statistics"]["by_category"].items(), key=lambda x: -x[1]):
        report += f"| {cat} | {count} |\n"
    
    report += "\n## Top 50 Most Confident Mappings\n\n"
    report += "| # | Voynich | Decoded | Latin | English | Confidence |\n"
    report += "|---|---------|---------|-------|---------|------------|\n"
    
    for i, e in enumerate(entries_list[:50], 1):
        report += f"| {i} | `{e['voynich']}` | {e['decoded']} | {e['latin']} | {e['english']} | {e['confidence']:.2f} |\n"
    
    report += "\n## Phonetic Key (Confirmed)\n\n"
    report += "| Voynich | Latin | Confidence |\n"
    report += "|---------|-------|------------|\n"
    
    confirmed_chars = [("o", "a"), ("h", "r"), ("9", "s"), ("k", "n"), ("c", "c"), ("7", "l"), ("m", "m")]
    for v, l in confirmed_chars:
        report += f"| {v} | {l} | CONFIRMED |\n"
    
    strong_chars = [("a", "e"), ("e", "i"), ("8", "d"), ("1", "t"), ("4", "qu"), ("y", "i"), ("2", "b")]
    for v, l in strong_chars:
        report += f"| {v} | {l} | STRONG |\n"
    
    report += "\n## Abbreviation System\n\n"
    report += "| Voynich Ending | Latin Equivalent |\n"
    report += "|----------------|------------------|\n"
    for v, l in ABBREVIATIONS.items():
        report += f"| {v} | {l} |\n"
    
    report += "\n## Usage Instructions\n\n"
    report += """```python
import json

# Load dictionary
with open('results/master_dictionary.json') as f:
    master = json.load(f)

# Look up a word
def lookup(word):
    for e in master['entries']:
        if e['voynich'] == word:
            return e
    return None

# Example
result = lookup('o4o')
print(result)  # {'voynich': 'o4o', 'latin': 'aqua', 'english': 'water', ...}
```
"""
    
    with open("results/master_dictionary_report.md", "w") as f:
        f.write(report)
    print("Saved master_dictionary_report.md")
    
    print("\n=== Summary ===")
    print(f"Total entries: {len(entries_list)}")
    print(f"High confidence (≥0.8): {master_dict['statistics']['high_confidence']}")
    print(f"Categories: {list(by_category.keys())}")
    
    print("\n=== Sample Lookups ===")
    test_words = ["o4o", "8am", "oh9", "4ohan", "9"]
    for w in test_words:
        res = lookup(w, entries)
        if res:
            print(f"  {w} → {res['latin']} ({res['english']}) [{res['confidence']:.2f}]")
    
    print("\n=== Reverse Lookup: 'aqua' ===")
    for r in reverse_lookup("aqua", entries):
        print(f"  {r['voynich']} [{r['confidence']:.2f}]")

if __name__ == "__main__":
    main()



