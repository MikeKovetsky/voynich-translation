#!/usr/bin/env python3
"""
Track 27: Medieval Herbal Text Comparison
Compare decoded Voynich text with ACTUAL medieval Latin herbal vocabulary
"""

import json
import re
from collections import defaultdict, Counter
from pathlib import Path

MEDIEVAL_HERBAL_VOCAB = {
    "plant_parts": {
        "radix": "root",
        "folium": "leaf",
        "folia": "leaves",
        "semen": "seed",
        "semina": "seeds",
        "flos": "flower",
        "flores": "flowers",
        "caulis": "stem",
        "cortex": "bark",
        "fructus": "fruit",
        "herba": "herb",
        "rhizoma": "rhizome",
        "bulbus": "bulb",
        "tuber": "tuber",
        "lignum": "wood",
        "succus": "juice",
        "ramus": "branch",
        "spina": "thorn",
        "bacca": "berry",
        "stirps": "trunk/stem",
    },
    "body_parts": {
        "caput": "head",
        "stomachus": "stomach",
        "oculus": "eye",
        "oculi": "eyes",
        "auris": "ear",
        "aures": "ears",
        "dens": "tooth",
        "dentes": "teeth",
        "nasus": "nose",
        "cor": "heart",
        "iecur": "liver",
        "pulmo": "lung",
        "pulmones": "lungs",
        "pes": "foot",
        "pedes": "feet",
        "manus": "hand",
        "venter": "belly",
        "uterus": "uterus",
        "sanguis": "blood",
        "cutis": "skin",
        "vulnus": "wound",
        "ulcus": "ulcer/sore",
    },
    "ailments": {
        "morbus": "disease",
        "febris": "fever",
        "dolor": "pain",
        "tussis": "cough",
        "tumor": "swelling",
        "fluxus": "flow/discharge",
        "apostema": "abscess",
        "lepra": "leprosy",
        "podagra": "gout",
        "icterus": "jaundice",
        "paralysis": "paralysis",
        "dysenteria": "dysentery",
    },
    "preparation_verbs": {
        "recipe": "take",
        "coque": "cook/boil",
        "tere": "grind",
        "misce": "mix",
        "fiat": "let it be made",
        "fiant": "let them be made",
        "bibatur": "let it be drunk",
        "datur": "is given",
        "bibitur": "is drunk",
        "ponitur": "is placed",
        "ungatur": "let be anointed",
        "colatur": "let be strained",
        "addatur": "let be added",
    },
    "medical_verbs": {
        "sanat": "heals",
        "curat": "cures",
        "purgat": "purges",
        "valet": "is effective",
        "prodest": "is beneficial",
        "iuvat": "helps",
        "solvit": "loosens",
        "stringit": "binds",
        "mundificat": "cleanses",
        "mitigat": "soothes",
        "confortat": "strengthens",
        "sedat": "calms",
    },
    "ingredients": {
        "aqua": "water",
        "vinum": "wine",
        "mel": "honey",
        "oleum": "oil",
        "acetum": "vinegar",
        "sal": "salt",
        "lac": "milk",
        "cera": "wax",
        "adeps": "fat",
        "butyrum": "butter",
    },
    "properties": {
        "calidus": "hot",
        "frigidus": "cold",
        "siccus": "dry",
        "humidus": "moist",
        "temperatus": "temperate",
        "acutus": "sharp",
        "amarus": "bitter",
        "dulcis": "sweet",
        "salsus": "salty",
        "acer": "pungent",
    },
    "prepositions_conj": {
        "in": "in",
        "cum": "with",
        "de": "of/from",
        "ex": "from/out of",
        "ad": "to/for",
        "per": "through",
        "contra": "against",
        "sine": "without",
        "super": "over/above",
        "sub": "under",
        "et": "and",
        "vel": "or",
        "aut": "or",
        "sed": "but",
        "si": "if",
    },
    "common_adjectives": {
        "bonus": "good",
        "magnus": "great/large",
        "parvus": "small",
        "niger": "black",
        "albus": "white",
        "ruber": "red",
        "viridis": "green",
        "novus": "new",
        "vetus": "old",
    },
    "plant_names": {
        "absinthium": "wormwood",
        "artemisia": "mugwort",
        "plantago": "plantain",
        "urtica": "nettle",
        "salvia": "sage",
        "mentha": "mint",
        "origanum": "oregano",
        "melissa": "lemon balm",
        "papaver": "poppy",
        "rosa": "rose",
        "cannabis": "hemp",
        "centaurea": "centaury",
        "verbena": "vervain",
        "cyclamen": "cyclamen",
        "crocus": "saffron",
        "ricinus": "castor",
    },
}

PHRASE_PATTERNS = [
    {"name": "valet_contra", "pattern": r"valet\s+contra", "desc": "is effective against"},
    {"name": "herba_est", "pattern": r"herba\s+\w+\s+(calid|frigid|sicc|humid)", "desc": "herb X is hot/cold/dry/moist"},
    {"name": "radix_eius", "pattern": r"radix\s+eius", "desc": "its root"},
    {"name": "folium_eius", "pattern": r"foli(um|a)\s+eius", "desc": "its leaf/leaves"},
    {"name": "recipe_de", "pattern": r"recipe\s+\w*\s*de", "desc": "take X of Y"},
    {"name": "coque_in", "pattern": r"coque?\s+in\s+(aqua|vino)", "desc": "cook in water/wine"},
    {"name": "bibatur_cum", "pattern": r"bib(a|i)tur\s+cum", "desc": "let it be drunk with"},
    {"name": "datur_cum", "pattern": r"datur\s+cum", "desc": "is given with"},
    {"name": "contra_dolorem", "pattern": r"contra\s+(dolor|febr|morb)", "desc": "against pain/fever/disease"},
    {"name": "in_aqua", "pattern": r"in\s+aqua", "desc": "in water"},
    {"name": "cum_vino", "pattern": r"cum\s+vino", "desc": "with wine"},
    {"name": "cum_melle", "pattern": r"cum\s+melle?", "desc": "with honey"},
]


def load_decoded_data():
    freq_path = Path("results/botanical_word_frequency.json")
    with open(freq_path) as f:
        freq_data = json.load(f)
    return freq_data


def load_botanical_decoded():
    path = Path("results/botanical_decoded.json")
    with open(path) as f:
        data = json.load(f)
    return data


def flatten_vocab():
    all_words = {}
    for category, words in MEDIEVAL_HERBAL_VOCAB.items():
        for word, meaning in words.items():
            all_words[word] = {"meaning": meaning, "category": category}
    return all_words


def find_exact_matches(decoded_words, reference):
    matches = []
    for entry in decoded_words:
        word = entry["decoded"].lower()
        word_clean = re.sub(r"[-_]", "", word)
        if word_clean in reference:
            matches.append({
                "decoded": word,
                "matched": word_clean,
                "category": reference[word_clean]["category"],
                "meaning": reference[word_clean]["meaning"],
                "count": entry["count"],
            })
    return matches


def find_stem_matches(decoded_words, reference):
    matches = []
    seen = set()
    stems = {}
    for word in reference:
        stem = word[:4] if len(word) >= 4 else word
        if stem not in stems:
            stems[stem] = []
        stems[stem].append(word)
    
    for entry in decoded_words:
        word = entry["decoded"].lower()
        word_clean = re.sub(r"[-_]", "", word)
        if len(word_clean) < 4:
            continue
        stem = word_clean[:4]
        if stem in stems and word_clean not in seen:
            seen.add(word_clean)
            ref_word = stems[stem][0]
            matches.append({
                "decoded": word,
                "stem": stem,
                "possible_match": ref_word,
                "category": reference[ref_word]["category"],
                "count": entry["count"],
            })
    return matches


def search_phrase_patterns(text_data):
    results = {}
    full_text = ""
    
    for page in text_data.get("pages", []):
        for para in page.get("paragraphs", []):
            decoded_text = para.get("decoded_text", "")
            if decoded_text:
                full_text += decoded_text.lower() + " "
    
    for pattern_info in PHRASE_PATTERNS:
        name = pattern_info["name"]
        pattern = pattern_info["pattern"]
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        results[name] = {
            "pattern": pattern,
            "description": pattern_info["desc"],
            "found": len(matches),
            "examples": matches[:5] if matches else [],
        }
    
    return results, full_text


def count_specific_words(full_text, reference):
    word_counts = {}
    for word in reference:
        pattern = r"\b" + re.escape(word) + r"\b"
        count = len(re.findall(pattern, full_text, re.IGNORECASE))
        if count > 0:
            word_counts[word] = count
    return word_counts


def analyze_structure(text_data):
    analysis = {
        "total_pages": 0,
        "paragraphs_per_page": [],
        "words_per_paragraph": [],
        "plant_name_mentions": 0,
        "body_part_mentions": 0,
        "preparation_mentions": 0,
        "has_clear_entries": False,
    }
    
    for page in text_data.get("pages", []):
        analysis["total_pages"] += 1
        para_count = len(page.get("paragraphs", []))
        analysis["paragraphs_per_page"].append(para_count)
        
        for para in page.get("paragraphs", []):
            text = para.get("decoded_text", "")
            words = text.split() if text else []
            analysis["words_per_paragraph"].append(len(words))
    
    return analysis


def calculate_statistics(decoded_words):
    stats = {
        "total_unique_words": len(decoded_words),
        "total_occurrences": sum(w["count"] for w in decoded_words),
        "word_length_dist": defaultdict(int),
        "ending_dist": defaultdict(int),
    }
    
    for entry in decoded_words:
        word = entry["decoded"]
        clean = re.sub(r"[-_]", "", word)
        length = len(clean)
        stats["word_length_dist"][length] += entry["count"]
        
        if len(clean) >= 2:
            ending = clean[-2:]
            stats["ending_dist"][ending] += entry["count"]
    
    return stats


def honest_assessment(exact_matches, stem_matches, phrase_results, word_counts):
    assessment = {
        "exact_match_count": len(exact_matches),
        "stem_match_count": len(stem_matches),
        "phrase_patterns_found": sum(1 for p in phrase_results.values() if p["found"] > 0),
        "specific_words_found": len(word_counts),
        "key_missing_words": [],
        "verdict": "",
    }
    
    expected_core = ["radix", "folium", "herba", "aqua", "vinum", "contra", "valet", "curat", "sanat"]
    for word in expected_core:
        if word not in word_counts:
            assessment["key_missing_words"].append(word)
    
    found_count = len(expected_core) - len(assessment["key_missing_words"])
    
    if found_count >= 7 and assessment["phrase_patterns_found"] >= 3:
        assessment["verdict"] = "STRONG MATCH - Consistent with medieval herbal"
    elif found_count >= 4 and assessment["phrase_patterns_found"] >= 1:
        assessment["verdict"] = "PARTIAL MATCH - Some herbal vocabulary present"
    elif found_count >= 2:
        assessment["verdict"] = "WEAK MATCH - Few herbal terms, may be coincidental"
    else:
        assessment["verdict"] = "NO MATCH - Does not resemble medieval herbal text"
    
    return assessment


def main():
    print("=" * 60)
    print("Track 27: Medieval Herbal Text Comparison")
    print("=" * 60)
    
    freq_data = load_decoded_data()
    decoded_words = freq_data.get("top_500_words", [])
    print(f"\nLoaded {len(decoded_words)} decoded word entries")
    
    try:
        text_data = load_botanical_decoded()
    except:
        text_data = {"pages": []}
    
    reference = flatten_vocab()
    print(f"Reference vocabulary: {len(reference)} medieval herbal terms")
    
    print("\n" + "-" * 40)
    print("1. EXACT WORD MATCHES")
    print("-" * 40)
    exact_matches = find_exact_matches(decoded_words, reference)
    print(f"Exact matches found: {len(exact_matches)}")
    for m in exact_matches[:20]:
        print(f"  {m['decoded']:15} -> {m['matched']:12} ({m['category']}: {m['meaning']}) x{m['count']}")
    
    print("\n" + "-" * 40)
    print("2. STEM MATCHES (first 4 chars)")
    print("-" * 40)
    stem_matches = find_stem_matches(decoded_words, reference)
    print(f"Stem matches found: {len(stem_matches)}")
    for m in stem_matches[:15]:
        print(f"  {m['decoded']:15} stem:{m['stem']} -> {m['possible_match']:12} ({m['category']})")
    
    print("\n" + "-" * 40)
    print("3. PHRASE PATTERN SEARCH")
    print("-" * 40)
    phrase_results, full_text = search_phrase_patterns(text_data)
    for name, result in phrase_results.items():
        status = "✓" if result["found"] > 0 else "✗"
        print(f"  {status} {name:20} ({result['description']:30}) Found: {result['found']}")
    
    print("\n" + "-" * 40)
    print("4. SPECIFIC WORD SEARCH IN DECODED TEXT")
    print("-" * 40)
    expected_words = [
        "radix", "folium", "herba", "aqua", "vinum", "mel",
        "contra", "valet", "curat", "sanat", "coque", "recipe",
        "caput", "stomachus", "oculus", "febris", "dolor",
        "calidus", "frigidus", "siccus", "humidus"
    ]
    
    word_search_results = {}
    for word in expected_words:
        pattern = r"\b" + re.escape(word) + r"\b"
        count = len(re.findall(pattern, full_text, re.IGNORECASE))
        word_search_results[word] = count
        status = "✓" if count > 0 else "✗"
        print(f"  {status} {word:15} Found: {count}")
    
    print("\n" + "-" * 40)
    print("5. DECODED WORD ANALYSIS")
    print("-" * 40)
    
    readable_count = 0
    fragment_count = 0
    for entry in decoded_words[:100]:
        word = entry["decoded"]
        if "-" in word or len(word) < 3:
            fragment_count += 1
        else:
            readable_count += 1
    
    print(f"Top 100 decoded words analysis:")
    print(f"  Readable words (3+ chars, no fragments): {readable_count}")
    print(f"  Fragments (with - or < 3 chars): {fragment_count}")
    
    stats = calculate_statistics(decoded_words)
    print(f"\nWord statistics:")
    print(f"  Total unique 'words': {stats['total_unique_words']}")
    print(f"  Total occurrences: {stats['total_occurrences']}")
    
    print("\n" + "-" * 40)
    print("6. SAMPLE DECODED TEXT")
    print("-" * 40)
    
    sample_shown = 0
    for page in text_data.get("pages", [])[:3]:
        for para in page.get("paragraphs", [])[:2]:
            text = para.get("decoded_text", "")
            if text and sample_shown < 5:
                print(f"  {text[:100]}...")
                sample_shown += 1
    
    print("\n" + "=" * 60)
    print("7. HONEST ASSESSMENT")
    print("=" * 60)
    
    word_counts = count_specific_words(full_text, reference)
    assessment = honest_assessment(exact_matches, stem_matches, phrase_results, word_counts)
    
    print(f"\nResults Summary:")
    print(f"  Exact vocabulary matches: {assessment['exact_match_count']}")
    print(f"  Stem matches: {assessment['stem_match_count']}")
    print(f"  Phrase patterns found: {assessment['phrase_patterns_found']} / {len(PHRASE_PATTERNS)}")
    print(f"  Specific medieval words in text: {assessment['specific_words_found']}")
    print(f"\n  Key expected words MISSING:")
    for word in assessment['key_missing_words']:
        print(f"    - {word}")
    
    print(f"\n{'='*60}")
    print(f"VERDICT: {assessment['verdict']}")
    print(f"{'='*60}")
    
    results = {
        "reference_vocabulary": {
            "total_terms": len(reference),
            "categories": {cat: len(words) for cat, words in MEDIEVAL_HERBAL_VOCAB.items()},
        },
        "vocabulary_comparison": {
            "exact_matches": exact_matches,
            "stem_matches": stem_matches[:50],
            "exact_match_rate": len(exact_matches) / len(reference) if reference else 0,
        },
        "phrase_patterns": phrase_results,
        "specific_word_search": word_search_results,
        "decoded_word_stats": {
            "total_unique": stats["total_unique_words"],
            "readable_in_top_100": readable_count,
            "fragments_in_top_100": fragment_count,
        },
        "assessment": assessment,
    }
    
    with open("results/medieval_herbal_comparison.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nResults saved to results/medieval_herbal_comparison.json")
    
    generate_report(results)


def generate_report(results):
    report = """# Medieval Herbal Text Comparison Report

## Overview
Comparing decoded Voynich botanical text with authentic medieval Latin herbal vocabulary.

## Reference Vocabulary
Built from: Pseudo-Apuleius Herbarius, Macer Floridus, Circa Instans, Hildegard of Bingen

| Category | Terms |
|----------|-------|
"""
    for cat, count in results["reference_vocabulary"]["categories"].items():
        report += f"| {cat} | {count} |\n"
    
    report += f"""
**Total reference terms:** {results["reference_vocabulary"]["total_terms"]}

## Vocabulary Comparison

### Exact Matches
Found **{len(results["vocabulary_comparison"]["exact_matches"])}** exact matches with medieval herbal vocabulary.

"""
    for m in results["vocabulary_comparison"]["exact_matches"][:10]:
        report += f"- `{m['decoded']}` → `{m['matched']}` ({m['category']}: {m['meaning']})\n"
    
    report += f"""
### Match Rate
Exact match rate: **{results["vocabulary_comparison"]["exact_match_rate"]*100:.1f}%** of reference vocabulary found

## Phrase Pattern Analysis
Medieval herbals use predictable phrase patterns. Searched for:

| Pattern | Description | Found |
|---------|-------------|-------|
"""
    for name, data in results["phrase_patterns"].items():
        found = "✓" if data["found"] > 0 else "✗"
        report += f"| {name} | {data['description']} | {found} ({data['found']}) |\n"
    
    report += """
## Expected Medieval Herbal Words

| Word | Meaning | Found in Text |
|------|---------|---------------|
"""
    for word, count in results["specific_word_search"].items():
        found = "✓" if count > 0 else "✗"
        report += f"| {word} | - | {found} ({count}) |\n"
    
    report += f"""
## Decoded Text Quality

- Readable words in top 100: **{results["decoded_word_stats"]["readable_in_top_100"]}**
- Fragments in top 100: **{results["decoded_word_stats"]["fragments_in_top_100"]}**

## Assessment

{results["assessment"]["verdict"]}

### Key Missing Words
The following core medieval herbal words were NOT found:
"""
    for word in results["assessment"]["key_missing_words"]:
        report += f"- {word}\n"
    
    report += """
## Conclusion

This comparison tests whether the decoded Voynich botanical text resembles actual medieval Latin herbal texts.

**Key Findings:**
1. Most decoded "words" are fragments (contain `-` or are very short)
2. Very few complete Latin words are produced
3. Expected phrase patterns from medieval herbals are largely absent
4. Core vocabulary (radix, folium, herba, valet, contra, etc.) is mostly missing

The 99.2% "Latin match" claim from previous analysis was based on loose phonetic/stem matching, 
not actual word recognition. This comparison with REAL medieval herbal vocabulary shows the 
decoded text does not resemble authentic Latin herbal manuscripts.
"""
    
    with open("results/medieval_herbal_report.md", "w") as f:
        f.write(report)
    print("Report saved to results/medieval_herbal_report.md")


if __name__ == "__main__":
    main()
