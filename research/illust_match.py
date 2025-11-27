#!/usr/bin/env python3
"""Track 57: Illustration Ground Truth Test
Check if decoded words match what's visible in manuscript illustrations."""

import json
import re
from collections import defaultdict

EVA_FILE = "data/eva_ivtff.txt"
DICT_FILE = "results/hybrid_dictionary.json"

VISUAL_DESCRIPTIONS = {
    "f2v": {
        "elements": [
            "large_round_green_leaf",
            "single_stem",
            "small_flower_top",
            "green_color"
        ],
        "absent": ["roots", "red_color", "blue_color", "multiple_plants"],
        "description": "Single plant with large round GREEN leaf, single stem, small 3-lobed flower at top"
    },
    "f3r": {
        "elements": [
            "striped_leaves_red_green",
            "wavy_leaves",
            "prominent_brown_roots",
            "single_stem",
            "red_color",
            "green_color",
            "brown_color"
        ],
        "absent": ["blue_color", "flowers", "round_leaves"],
        "description": "Plant with alternating RED and GREEN striped wavy leaves, prominent BROWN ROOTS at bottom"
    },
    "f3v": {
        "elements": [
            "two_plants",
            "blue_flower_heads",
            "spiky_green_leaves",
            "brown_root",
            "feathery_leaves_left",
            "blue_color",
            "green_color",
            "brown_color"
        ],
        "absent": ["red_striped_leaves", "round_leaves"],
        "description": "TWO plants: left has feathery leaves, right has BLUE flower heads, spiky green leaves, brown root"
    }
}

SEMANTIC_MAPPINGS = {
    "leaf": ["leaf", "leaves", "green", "foliage"],
    "flower": ["flower", "bloom", "blossom", "flora"],
    "root": ["root", "radix", "shoresh"],
    "stem": ["stem", "stalk", "trunk"],
    "seed": ["seed", "semen"],
    "red": ["red", "blood", "dam", "crimson"],
    "blue": ["blue", "azure"],
    "green": ["green", "verdant"],
    "earth": ["earth", "terra", "soil", "ground"],
    "plant": ["plant", "herb", "herba"],
    "two": ["two", "pair", "double"],
    "sick": ["sick", "disease", "illness", "choleh"],
    "cure": ["cure", "heal", "medicine", "remedy"],
    "extract": ["extract", "draw out", "pull"],
    "hole": ["hole", "pierce", "opening"],
    "fig": ["fig", "ficus", "tena"],
    "heart": ["heart", "cuore", "cor"],
}


def load_dict():
    with open(DICT_FILE) as f:
        data = json.load(f)
    return data["entries"]


def parse_page(folio):
    words = []
    with open(EVA_FILE) as f:
        for line in f:
            if line.startswith(f"<{folio}.") and ";H>" in line:
                match = re.search(r';H>\s*(.+?)(?:<|$)', line)
                if match:
                    text = match.group(1).strip()
                    text = re.sub(r'<[^>]*>', '', text)
                    text = re.sub(r'[!\?\-]', '.', text)
                    for word in text.split('.'):
                        word = word.strip()
                        if word and len(word) > 1:
                            words.append(word)
    return words


def translate_word(word, dictionary):
    if word in dictionary:
        entry = dictionary[word]
        return entry.get("primary_meaning", "?")
    for variant_word, entry in dictionary.items():
        variants = entry.get("variants", [])
        if word in variants:
            return entry.get("primary_meaning", "?")
    return None


def check_visual_match(translation, visual_elements, absent_elements):
    if not translation:
        return "UNKNOWN"
    
    trans_lower = translation.lower()
    
    for element in visual_elements:
        for category, keywords in SEMANTIC_MAPPINGS.items():
            if any(kw in trans_lower for kw in keywords):
                if category in element or element in category:
                    return "MATCH"
                element_parts = element.replace("_", " ").split()
                if category in element_parts:
                    return "MATCH"
    
    if "root" in trans_lower:
        if any("root" in e for e in visual_elements):
            return "MATCH"
        if "roots" in absent_elements:
            return "MISMATCH"
    
    if "flower" in trans_lower:
        if any("flower" in e for e in visual_elements):
            return "MATCH"
        if "flowers" in absent_elements:
            return "MISMATCH"
    
    if "blood" in trans_lower or "red" in trans_lower:
        if any("red" in e for e in visual_elements):
            return "MATCH"
        if "red_color" in absent_elements:
            return "MISMATCH"
    
    if "blue" in trans_lower:
        if any("blue" in e for e in visual_elements):
            return "MATCH"
        if "blue_color" in absent_elements:
            return "MISMATCH"
    
    gram_words = ["the", "of", "from", "and", "to", "for", "with"]
    if any(gw == trans_lower for gw in gram_words):
        return "GRAMMAR"
    
    return "UNKNOWN"


def analyze_page(folio, dictionary):
    words = parse_page(folio)
    visual = VISUAL_DESCRIPTIONS[folio]
    
    results = {
        "folio": folio,
        "visual_description": visual["description"],
        "visual_elements": visual["elements"],
        "absent_elements": visual["absent"],
        "total_words": len(words),
        "word_analysis": [],
        "matches": [],
        "mismatches": [],
        "unknown": [],
        "grammar": [],
        "not_in_dict": []
    }
    
    word_counts = defaultdict(int)
    for w in words:
        word_counts[w] += 1
    
    seen = set()
    for word in words:
        if word in seen:
            continue
        seen.add(word)
        
        translation = translate_word(word, dictionary)
        
        if translation:
            status = check_visual_match(translation, visual["elements"], visual["absent"])
            entry = {
                "word": word,
                "translation": translation,
                "count": word_counts[word],
                "status": status
            }
            results["word_analysis"].append(entry)
            
            if status == "MATCH":
                results["matches"].append(entry)
            elif status == "MISMATCH":
                results["mismatches"].append(entry)
            elif status == "GRAMMAR":
                results["grammar"].append(entry)
            else:
                results["unknown"].append(entry)
        else:
            results["not_in_dict"].append({
                "word": word,
                "count": word_counts[word]
            })
    
    total_content = len(results["matches"]) + len(results["mismatches"])
    if total_content > 0:
        results["match_score"] = len(results["matches"]) / total_content
    else:
        results["match_score"] = None
    
    return results


def main():
    print("=" * 60)
    print("TRACK 57: Illustration Ground Truth Test")
    print("=" * 60)
    
    dictionary = load_dict()
    print(f"\nLoaded dictionary with {len(dictionary)} entries")
    
    pages = ["f2v", "f3r", "f3v"]
    all_results = {
        "pages_tested": pages,
        "per_page": {},
        "overall_matches": 0,
        "overall_mismatches": 0
    }
    
    for folio in pages:
        print(f"\n{'=' * 60}")
        print(f"Analyzing {folio.upper()}")
        print("=" * 60)
        
        results = analyze_page(folio, dictionary)
        all_results["per_page"][folio] = results
        
        print(f"\nVisual: {results['visual_description']}")
        print(f"Total words on page: {results['total_words']}")
        print(f"Unique words: {len(results['word_analysis']) + len(results['not_in_dict'])}")
        print(f"Translated: {len(results['word_analysis'])}")
        
        print(f"\n--- MATCHES ({len(results['matches'])}) ---")
        for m in results["matches"]:
            print(f"  {m['word']} = '{m['translation']}' (x{m['count']})")
        
        print(f"\n--- MISMATCHES ({len(results['mismatches'])}) ---")
        for m in results["mismatches"]:
            print(f"  ❌ {m['word']} = '{m['translation']}' (x{m['count']})")
        
        print(f"\n--- GRAMMAR WORDS ({len(results['grammar'])}) ---")
        for m in results["grammar"][:5]:
            print(f"  {m['word']} = '{m['translation']}' (x{m['count']})")
        
        print(f"\n--- UNKNOWN/UNTESTABLE ({len(results['unknown'])}) ---")
        for m in results["unknown"][:10]:
            print(f"  {m['word']} = '{m['translation']}' (x{m['count']})")
        
        if results["match_score"] is not None:
            print(f"\n*** MATCH SCORE: {results['match_score']:.1%} ***")
        
        all_results["overall_matches"] += len(results["matches"])
        all_results["overall_mismatches"] += len(results["mismatches"])
    
    total = all_results["overall_matches"] + all_results["overall_mismatches"]
    if total > 0:
        overall = all_results["overall_matches"] / total
        all_results["overall_score"] = overall
        if overall >= 0.7:
            all_results["confidence"] = "high"
        elif overall >= 0.4:
            all_results["confidence"] = "medium"
        else:
            all_results["confidence"] = "low"
    else:
        all_results["overall_score"] = None
        all_results["confidence"] = "insufficient_data"
    
    print("\n" + "=" * 60)
    print("OVERALL RESULTS")
    print("=" * 60)
    print(f"Total matches: {all_results['overall_matches']}")
    print(f"Total mismatches: {all_results['overall_mismatches']}")
    if all_results["overall_score"] is not None:
        print(f"Overall score: {all_results['overall_score']:.1%}")
    print(f"Confidence: {all_results['confidence']}")
    
    with open("results/illustration_match.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print("\nSaved: results/illustration_match.json")
    
    generate_report(all_results)
    
    return all_results


def generate_report(results):
    lines = []
    lines.append("# Track 57: Illustration Ground Truth Test")
    lines.append("")
    lines.append("## Purpose")
    lines.append("Test if our decoded words match what we SEE in the manuscript illustrations.")
    lines.append("This is the ultimate validation - does 'root' appear near root drawings?")
    lines.append("")
    
    lines.append("## Test Pages")
    for folio in results["pages_tested"]:
        page = results["per_page"][folio]
        lines.append(f"\n### {folio.upper()}")
        lines.append(f"**Visual Description:** {page['visual_description']}")
        lines.append(f"\n**Key Visual Elements:**")
        for elem in page["visual_elements"]:
            lines.append(f"- {elem.replace('_', ' ')}")
        
        lines.append(f"\n**Translation Analysis:**")
        lines.append(f"- Total words: {page['total_words']}")
        lines.append(f"- Matches: {len(page['matches'])}")
        lines.append(f"- Mismatches: {len(page['mismatches'])}")
        lines.append(f"- Grammar: {len(page['grammar'])}")
        lines.append(f"- Unknown: {len(page['unknown'])}")
        
        if page["matches"]:
            lines.append(f"\n**✅ MATCHES (word meaning IS visible):**")
            for m in page["matches"]:
                lines.append(f"- `{m['word']}` = '{m['translation']}' (appears {m['count']}x)")
        
        if page["mismatches"]:
            lines.append(f"\n**❌ MISMATCHES (word meaning NOT visible):**")
            for m in page["mismatches"]:
                lines.append(f"- `{m['word']}` = '{m['translation']}' (appears {m['count']}x)")
        
        if page["match_score"] is not None:
            lines.append(f"\n**Page Score: {page['match_score']:.1%}**")
    
    lines.append("\n## Overall Results")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total Matches | {results['overall_matches']} |")
    lines.append(f"| Total Mismatches | {results['overall_mismatches']} |")
    if results["overall_score"] is not None:
        lines.append(f"| Overall Score | {results['overall_score']:.1%} |")
    lines.append(f"| Confidence | {results['confidence']} |")
    
    lines.append("\n## Interpretation")
    lines.append("")
    
    score = results.get("overall_score")
    if score is None:
        lines.append("**INSUFFICIENT DATA**: Not enough content words could be matched to visual elements.")
        lines.append("Most words are either grammar particles or have meanings we can't verify visually.")
    elif score >= 0.7:
        lines.append("**HIGH CONFIDENCE**: Our translations match the illustrations!")
        lines.append("When we decode plant-related words, they correspond to what's drawn.")
    elif score >= 0.4:
        lines.append("**MEDIUM CONFIDENCE**: Mixed results.")
        lines.append("Some translations match, others don't. Could be:")
        lines.append("- Partial accuracy in our dictionary")
        lines.append("- Text describes more than just the drawing")
        lines.append("- Some wrong translations")
    else:
        lines.append("**LOW CONFIDENCE**: Our translations DON'T match the illustrations.")
        lines.append("This suggests our decoding may be wrong or the text is unrelated to the images.")
    
    lines.append("\n## Key Finding: 'Root' Word Test")
    lines.append("")
    lines.append("Our dictionary claims `shor` = 'root (shoresh)' from Hebrew.")
    lines.append("")
    f3r = results["per_page"].get("f3r", {})
    shor_found = any(m["word"] == "shor" for m in f3r.get("matches", []))
    if shor_found:
        lines.append("**✅ VALIDATED**: 'shor' appears on f3r which has PROMINENT ROOTS drawn!")
        lines.append("This is strong evidence our Hebrew root translation is correct.")
    else:
        matches = f3r.get("matches", [])
        if any("root" in m.get("translation", "").lower() for m in matches):
            lines.append("**✅ VALIDATED**: Root-related words found on page with roots!")
        else:
            lines.append("**⚠️ INCONCLUSIVE**: No direct root word match found.")
    
    lines.append("\n## Honest Assessment")
    lines.append("")
    lines.append("This test has limitations:")
    lines.append("1. We can only verify VISUAL concepts (colors, shapes, parts)")
    lines.append("2. Abstract words (sick, cure, extract) can't be visually verified")
    lines.append("3. Text may describe uses/properties not shown in drawings")
    lines.append("4. Small sample size (3 pages)")
    lines.append("")
    
    with open("results/illustration_match_report.md", "w") as f:
        f.write("\n".join(lines))
    print("Saved: results/illustration_match_report.md")


if __name__ == "__main__":
    main()



