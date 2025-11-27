"""
Track 86: Mine Non-Herbal Sections (Bio, Cosmo, Pharma)

Apply the "Unique Word Mining" algorithm to:
- Biological (f75-f84): Bathing nymphs -> Body parts? Bathing instructions?
- Cosmological (f67-f73): Zodiac/circles -> Timing/Calendar instructions?
- Pharmaceutical (f87-f102): Vials/roots -> Containers? Measurements?
"""

import json
import re
from collections import defaultdict
from pathlib import Path

EVA_FILE = Path("data/eva_ivtff.txt")
RESULTS_DIR = Path("results")

SECTIONS = {
    "biological": {
        "range": list(range(75, 85)),
        "hypothesis": "Body parts, bathing instructions, purification rituals",
        "expected_terms": ["body", "water", "bathe", "wash", "hand", "foot", "head"],
    },
    "cosmological": {
        "range": list(range(67, 74)),
        "hypothesis": "Timing, calendar, astronomical instructions",
        "expected_terms": ["month", "star", "day", "time", "season", "zodiac"],
    },
    "pharmaceutical": {
        "range": list(range(88, 103)),
        "hypothesis": "Containers, measurements, preparation methods",
        "expected_terms": ["vessel", "measure", "mix", "pour", "grind", "boil"],
    },
}

RECIPE_RANGE = list(range(103, 117))

HEBREW_BODYPARTS = {
    "yad": "hand", "regel": "foot", "rosh": "head", "lev": "heart",
    "ayin": "eye", "ozen": "ear", "af": "nose", "pe": "mouth",
    "guf": "body", "dam": "blood", "etzem": "bone", "basar": "flesh",
}

HEBREW_TIME = {
    "yom": "day", "layla": "night", "chodesh": "month", "shana": "year",
    "et": "time", "moed": "season", "shaon": "hour", "boker": "morning",
}

HEBREW_CONTAINERS = {
    "keli": "vessel", "kos": "cup", "kad": "jug", "tsalachat": "plate",
    "midah": "measure", "seah": "seah (measure)", "hin": "hin (measure)",
}


def load_eva_data():
    if not EVA_FILE.exists():
        raise FileNotFoundError(f"EVA file not found: {EVA_FILE}")
    
    folio_words = defaultdict(list)
    folio_lines = defaultdict(list)
    
    with open(EVA_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            
            m = re.match(r'<([^>]+);(\w)>\s*(.+)', line)
            if m:
                loc, transcriber, text = m.groups()
                if transcriber != 'H':
                    continue
                
                folio = loc.split('.')[0]
                text_clean = re.sub(r'[!?<>@$\[\]{}%\d]', '', text)
                words = re.split(r'[.\-=,\s]+', text_clean)
                words = [w.strip() for w in words if w.strip() and len(w.strip()) > 1]
                
                folio_words[folio].extend(words)
                folio_lines[folio].append({"loc": loc, "text": text, "words": words})
    
    return folio_words, folio_lines


def get_section_folios(page_range):
    folios = []
    for num in page_range:
        folios.append(f"f{num}r")
        folios.append(f"f{num}v")
    return folios


def build_rarity_index(folio_words):
    word_stats = defaultdict(lambda: {"count": 0, "folios": set()})
    
    for folio, words in folio_words.items():
        for word in words:
            word_stats[word]["count"] += 1
            word_stats[word]["folios"].add(folio)
    
    for word in word_stats:
        word_stats[word]["folios"] = sorted(word_stats[word]["folios"])
    
    return dict(word_stats)


def extract_section_rare_words(folio_words, rarity_index, section_folios, max_occurrences=5):
    section_words = set()
    section_word_counts = defaultdict(int)
    
    for folio in section_folios:
        if folio in folio_words:
            for word in folio_words[folio]:
                section_words.add(word)
                section_word_counts[word] += 1
    
    rare_words = []
    for word in section_words:
        stats = rarity_index.get(word, {"count": 0, "folios": []})
        
        if stats["count"] <= max_occurrences:
            other_folios = [f for f in stats["folios"] if f not in section_folios]
            in_section_only = len(other_folios) == 0
            
            rare_words.append({
                "word": word,
                "total_occurrences": stats["count"],
                "section_occurrences": section_word_counts[word],
                "in_section_only": in_section_only,
                "other_folios": other_folios
            })
    
    return sorted(rare_words, key=lambda x: (-x["in_section_only"], x["total_occurrences"]))


def crossref_with_recipes(rare_words, folio_lines, recipe_folios):
    recipe_words = set()
    for folio in recipe_folios:
        if folio in folio_lines:
            for line_data in folio_lines[folio]:
                recipe_words.update(line_data["words"])
    
    crossref_results = []
    
    for rare in rare_words:
        word = rare["word"]
        
        recipe_folios_found = [f for f in rare["other_folios"] if f in recipe_folios]
        
        if recipe_folios_found or word in recipe_words:
            recipe_contexts = []
            for rf in recipe_folios:
                if rf in folio_lines:
                    for line_data in folio_lines[rf]:
                        if word in line_data["words"]:
                            context_words = line_data["words"]
                            idx = context_words.index(word)
                            start = max(0, idx - 2)
                            end = min(len(context_words), idx + 3)
                            context = " ".join(context_words[start:end])
                            recipe_contexts.append({
                                "folio": rf,
                                "loc": line_data["loc"],
                                "context": context
                            })
            
            if recipe_contexts:
                confidence = "HIGH" if rare["in_section_only"] else "MEDIUM"
                if len(recipe_contexts) >= 3:
                    confidence = "HIGH"
                
                crossref_results.append({
                    "word": word,
                    "total_occurrences": rare["total_occurrences"],
                    "section_only": rare["in_section_only"],
                    "recipe_count": len(recipe_contexts),
                    "recipe_contexts": recipe_contexts[:5],
                    "confidence": confidence
                })
    
    return sorted(crossref_results, key=lambda x: (-int(x["section_only"]), -x["recipe_count"]))


def compute_skeleton(word):
    vowels = set('aeiou')
    return ''.join(c for c in word.lower() if c not in vowels)


def match_hebrew_patterns(word, term_dict):
    word_skel = compute_skeleton(word)
    matches = []
    
    for heb, eng in term_dict.items():
        heb_skel = compute_skeleton(heb)
        
        if heb_skel in word_skel or word_skel in heb_skel:
            matches.append({"hebrew": heb, "english": eng, "match_type": "skeleton"})
        elif len(word_skel) >= 3 and len(heb_skel) >= 3:
            if word_skel[:2] == heb_skel[:2]:
                matches.append({"hebrew": heb, "english": eng, "match_type": "prefix"})
    
    return matches


def analyze_section(section_name, section_info, folio_words, folio_lines, rarity_index, recipe_folios):
    section_folios = get_section_folios(section_info["range"])
    available = [f for f in section_folios if f in folio_words]
    
    print(f"\n   {section_name.upper()}: {len(available)} folios available")
    
    rare_words = extract_section_rare_words(folio_words, rarity_index, section_folios)
    print(f"   Found {len(rare_words)} rare words")
    
    crossref = crossref_with_recipes(rare_words, folio_lines, recipe_folios)
    print(f"   Cross-referenced: {len(crossref)} appear in recipes")
    
    if section_name == "biological":
        pattern_dict = HEBREW_BODYPARTS
    elif section_name == "cosmological":
        pattern_dict = HEBREW_TIME
    else:
        pattern_dict = HEBREW_CONTAINERS
    
    for item in crossref:
        item["hebrew_matches"] = match_hebrew_patterns(item["word"], pattern_dict)
    
    section_only_count = sum(1 for r in rare_words if r["in_section_only"])
    high_conf = sum(1 for c in crossref if c["confidence"] == "HIGH")
    
    return {
        "section": section_name,
        "hypothesis": section_info["hypothesis"],
        "folios_analyzed": available,
        "folio_count": len(available),
        "rare_words_found": len(rare_words),
        "section_specific_words": section_only_count,
        "recipe_crossrefs": len(crossref),
        "high_confidence": high_conf,
        "crossref_results": crossref,
        "top_rare_words": rare_words[:30]
    }


def generate_report(results):
    report = []
    report.append("# Track 86: Non-Herbal Section Mining Results\n")
    report.append("## Methodology\n")
    report.append("Apply **Unique Word Mining** to Biological, Cosmological, and Pharmaceutical sections.\n")
    report.append("Words RARE in these sections that ALSO appear in recipes = functional vocabulary.\n")
    
    report.append("## Summary\n")
    report.append("| Section | Folios | Rare Words | Section-Only | Recipe Crossrefs | High Conf |")
    report.append("|---------|--------|------------|--------------|------------------|-----------|")
    
    for section, data in results.items():
        report.append(f"| {section.title()} | {data['folio_count']} | {data['rare_words_found']} | "
                     f"{data['section_specific_words']} | {data['recipe_crossrefs']} | {data['high_confidence']} |")
    
    report.append("")
    
    for section, data in results.items():
        report.append(f"\n## {section.title()} Section\n")
        report.append(f"**Hypothesis**: {data['hypothesis']}\n")
        report.append(f"**Folios**: {', '.join(data['folios_analyzed'][:10])}...")
        report.append(f"\n### Recipe Cross-References\n")
        
        if data["crossref_results"]:
            report.append("| Word | Total | Recipe Count | Confidence | Hebrew Match |")
            report.append("|------|-------|--------------|------------|--------------|")
            
            for item in data["crossref_results"][:15]:
                heb_match = ""
                if item.get("hebrew_matches"):
                    heb_match = f"{item['hebrew_matches'][0]['hebrew']}={item['hebrew_matches'][0]['english']}"
                report.append(f"| `{item['word']}` | {item['total_occurrences']} | "
                             f"{item['recipe_count']} | {item['confidence']} | {heb_match} |")
            
            report.append("\n#### Sample Recipe Contexts\n")
            for item in data["crossref_results"][:5]:
                report.append(f"\n**`{item['word']}`**")
                for ctx in item["recipe_contexts"][:2]:
                    report.append(f"- {ctx['folio']}: _{ctx['context']}_")
        else:
            report.append("_No crossrefs found._\n")
        
        report.append(f"\n### Section-Specific Words (appear ONLY in {section})\n")
        specific = [w for w in data["top_rare_words"] if w["in_section_only"]]
        if specific:
            words = [f"`{w['word']}`" for w in specific[:20]]
            report.append(", ".join(words))
        else:
            report.append("_None found._")
    
    report.append("\n\n## Interpretation\n")
    
    total_crossrefs = sum(d["recipe_crossrefs"] for d in results.values())
    total_high = sum(d["high_confidence"] for d in results.values())
    
    report.append(f"- **Total recipe cross-references**: {total_crossrefs}")
    report.append(f"- **High confidence matches**: {total_high}")
    report.append("")
    
    if results["biological"]["recipe_crossrefs"] > 0:
        report.append("### Biological → Body Part/Ritual Terms ✓")
        report.append("Words from 'bathing nymphs' pages appearing in recipes suggest:")
        report.append("- Body parts mentioned in treatments")
        report.append("- Bathing/purification instructions referenced")
        report.append("")
    
    if results["cosmological"]["recipe_crossrefs"] > 0:
        report.append("### Cosmological → Timing Instructions ✓")
        report.append("Words from zodiac pages appearing in recipes suggest:")
        report.append("- 'Harvest in [month]' type instructions")
        report.append("- Astrological timing for remedies")
        report.append("")
    
    if results["pharmaceutical"]["recipe_crossrefs"] > 0:
        report.append("### Pharmaceutical → Container/Measurement Terms ✓")
        report.append("Words from vials pages appearing in recipes suggest:")
        report.append("- Container names for preparations")
        report.append("- Measurement units")
        report.append("")
    
    report.append("\n---\n")
    report.append("*Generated by Track 86: Mine Non-Herbal Sections*")
    
    return "\n".join(report)


def main():
    print("Track 86: Mine Non-Herbal Sections")
    print("=" * 50)
    
    print("\n1. Loading EVA transcription data...")
    folio_words, folio_lines = load_eva_data()
    print(f"   Loaded {len(folio_words)} folios")
    
    print("\n2. Building rarity index...")
    rarity_index = build_rarity_index(folio_words)
    print(f"   Total unique words: {len(rarity_index)}")
    
    recipe_folios = get_section_folios(RECIPE_RANGE)
    available_recipes = [f for f in recipe_folios if f in folio_words]
    print(f"\n3. Recipe section: {len(available_recipes)} folios")
    
    print("\n4. Analyzing sections...")
    results = {}
    
    for section_name, section_info in SECTIONS.items():
        results[section_name] = analyze_section(
            section_name, section_info, folio_words, folio_lines, rarity_index, recipe_folios
        )
    
    print("\n5. Saving results...")
    RESULTS_DIR.mkdir(exist_ok=True)
    
    output_data = {
        "biological_matches": results["biological"]["crossref_results"],
        "cosmological_matches": results["cosmological"]["crossref_results"],
        "pharmaceutical_matches": results["pharmaceutical"]["crossref_results"],
        "statistics": {
            section: {
                "folios": data["folio_count"],
                "rare_words": data["rare_words_found"],
                "section_specific": data["section_specific_words"],
                "recipe_crossrefs": data["recipe_crossrefs"],
                "high_confidence": data["high_confidence"]
            }
            for section, data in results.items()
        }
    }
    
    with open(RESULTS_DIR / "section_mining_full.json", 'w') as f:
        json.dump(output_data, f, indent=2)
    
    report = generate_report(results)
    with open(RESULTS_DIR / "section_mining_report.md", 'w') as f:
        f.write(report)
    
    print("\n" + "=" * 50)
    print("RESULTS SUMMARY")
    print("=" * 50)
    
    for section, data in results.items():
        print(f"\n{section.upper()}:")
        print(f"  Folios: {data['folio_count']}")
        print(f"  Rare words: {data['rare_words_found']}")
        print(f"  Recipe crossrefs: {data['recipe_crossrefs']}")
        print(f"  High confidence: {data['high_confidence']}")
        
        if data["crossref_results"]:
            print(f"  Top matches:")
            for item in data["crossref_results"][:3]:
                heb = ""
                if item.get("hebrew_matches"):
                    heb = f" (possible: {item['hebrew_matches'][0]['english']})"
                print(f"    - {item['word']}: {item['recipe_count']} recipe occurrences{heb}")
    
    total = sum(d["recipe_crossrefs"] for d in results.values())
    print(f"\n{'='*50}")
    print(f"TOTAL RECIPE CROSS-REFERENCES: {total}")
    print(f"{'='*50}")
    
    print("\nOutput files:")
    print("  - results/section_mining_full.json")
    print("  - results/section_mining_report.md")


if __name__ == "__main__":
    main()



