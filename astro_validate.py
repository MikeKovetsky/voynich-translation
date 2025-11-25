"""
Track 63: Astronomical Section Validation
Tests our dictionary on zodiac/astronomical pages.
"""

import json
import re
from collections import Counter
from pathlib import Path

import voynich_data as vd

DICT_FILE = Path("results/clean_dictionary.json")
OUTPUT_JSON = Path("results/astronomical_validation.json")
OUTPUT_MD = Path("results/astronomical_validation_report.md")

ZODIAC_FOLIOS = {
    "f70r1": "Pisces (light)",
    "f70v1": "Aries (dark)",
    "f70v2": "Aries (light)",
    "f71r": "Taurus (dark)",
    "f71v": "Taurus (light)",
    "f72r1": "Gemini (dark)",
    "f72r2": "Gemini (light)",
    "f72r3": "Cancer",
    "f72v1": "Libra",
    "f72v2": "Virgo",
    "f72v3": "Leo",
    "f73r": "Scorpio",
    "f73v": "Sagittarius",
}

ZODIAC_INFO = {
    "aries": {"latin": "aries", "hebrew": "טלה", "hebrew_trans": "taleh", "month_lat": "aprilis", "month_heb": "nisan"},
    "taurus": {"latin": "taurus", "hebrew": "שור", "hebrew_trans": "shor", "month_lat": "maius", "month_heb": "iyar"},
    "gemini": {"latin": "gemini", "hebrew": "תאומים", "hebrew_trans": "teomim", "month_lat": "iunius", "month_heb": "sivan"},
    "cancer": {"latin": "cancer", "hebrew": "סרטן", "hebrew_trans": "sartan", "month_lat": "iulius", "month_heb": "tammuz"},
    "leo": {"latin": "leo", "hebrew": "אריה", "hebrew_trans": "aryeh", "month_lat": "augustus", "month_heb": "av"},
    "virgo": {"latin": "virgo", "hebrew": "בתולה", "hebrew_trans": "betulah", "month_lat": "september", "month_heb": "elul"},
    "libra": {"latin": "libra", "hebrew": "מאזניים", "hebrew_trans": "moznayim", "month_lat": "october", "month_heb": "tishrei"},
    "scorpio": {"latin": "scorpius", "hebrew": "עקרב", "hebrew_trans": "akrav", "month_lat": "november", "month_heb": "cheshvan"},
    "sagittarius": {"latin": "sagittarius", "hebrew": "קשת", "hebrew_trans": "keshet", "month_lat": "december", "month_heb": "kislev"},
    "capricorn": {"latin": "capricornus", "hebrew": "גדי", "hebrew_trans": "gedi", "month_lat": "ianuarius", "month_heb": "tevet"},
    "aquarius": {"latin": "aquarius", "hebrew": "דלי", "hebrew_trans": "dli", "month_lat": "februarius", "month_heb": "shevat"},
    "pisces": {"latin": "pisces", "hebrew": "דגים", "hebrew_trans": "dagim", "month_lat": "martius", "month_heb": "adar"},
}

STAR_NAMES = {
    "aldebaran": {"constellation": "taurus", "hebrew": "עין השור", "arabic": "الدبران", "meaning": "follower"},
    "regulus": {"constellation": "leo", "hebrew": "לב האריה", "arabic": "قلب الأسد", "meaning": "heart of lion"},
    "spica": {"constellation": "virgo", "hebrew": "שיבולת", "arabic": "السماك", "meaning": "ear of wheat"},
    "antares": {"constellation": "scorpio", "hebrew": "לב העקרב", "arabic": "قلب العقرب", "meaning": "heart of scorpion"},
    "fomalhaut": {"constellation": "pisces", "hebrew": "פי הדג", "arabic": "فم الحوت", "meaning": "mouth of fish"},
    "deneb": {"constellation": "cygnus", "hebrew": "זנב", "arabic": "ذنب", "meaning": "tail"},
}

STAR_PATTERNS = {
    "aldebaran": ["aldn", "aldb", "dbr", "dbrn"],
    "regulus": ["rgl", "regl", "rglus"],
    "spica": ["spc", "spk", "shbl"],
    "antares": ["antr", "anrs", "akrb", "lev"],
    "fomalhaut": ["fmlh", "pmlh"],
}


def load_dictionary():
    with open(DICT_FILE) as f:
        data = json.load(f)
    return data["entries"]


def extract_words(text):
    text_clean = re.sub(r'[!?<>@$\d%]', '', text)
    words = re.split(r'[.\-=,\s]', text_clean)
    return [w for w in words if w and len(w) > 1]


def get_zodiac_text():
    pages = vd.get_eva_pages()
    result = {}
    
    for folio, sign in ZODIAC_FOLIOS.items():
        folio_data = {}
        for page_id, page_text in pages.items():
            if page_id.startswith(folio):
                for loc, text in page_text.items():
                    folio_data[loc] = text
        if not folio_data and folio in pages:
            folio_data = pages[folio]
        result[folio] = {"sign": sign, "lines": folio_data}
    
    return result


def translate_section(lines, dictionary):
    total_words = 0
    translated_words = 0
    translations = []
    word_freq = Counter()
    
    for loc, text in lines.items():
        words = extract_words(text)
        line_trans = []
        for w in words:
            total_words += 1
            word_freq[w] += 1
            if w in dictionary:
                translated_words += 1
                line_trans.append(f"{w}({dictionary[w]['meaning']})")
            else:
                line_trans.append(w)
        translations.append({"loc": loc, "original": text, "translated": " ".join(line_trans)})
    
    return {
        "total_words": total_words,
        "translated": translated_words,
        "coverage": translated_words / total_words if total_words > 0 else 0,
        "translations": translations,
        "word_freq": dict(word_freq.most_common(50))
    }


def find_label_words(lines):
    labels = []
    for loc, text in lines.items():
        if "@" in loc or "L" in loc.upper():
            words = extract_words(text)
            labels.extend(words)
    
    if not labels:
        all_words = []
        for text in lines.values():
            all_words.extend(extract_words(text))
        if all_words:
            labels = all_words[:5]
    
    return labels


def match_zodiac_name(word, sign):
    sign_key = sign.split()[0].lower()
    if sign_key not in ZODIAC_INFO:
        return None
    
    info = ZODIAC_INFO[sign_key]
    matches = {}
    
    word_lower = word.lower()
    for name_type, name in [("latin", info["latin"]), ("hebrew_trans", info["hebrew_trans"])]:
        score = simple_match_score(word_lower, name)
        if score > 0.3:
            matches[name_type] = {"name": name, "score": score}
    
    month_lat = info["month_lat"]
    month_score = simple_match_score(word_lower, month_lat)
    if month_score > 0.3:
        matches["month_latin"] = {"name": month_lat, "score": month_score}
    
    return matches if matches else None


def simple_match_score(word1, word2):
    if not word1 or not word2:
        return 0.0
    
    set1 = set(word1)
    set2 = set(word2)
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    jaccard = intersection / union if union > 0 else 0
    
    len_diff = abs(len(word1) - len(word2)) / max(len(word1), len(word2))
    len_score = 1 - len_diff
    
    prefix_match = 0
    for i in range(min(len(word1), len(word2), 3)):
        if word1[i] == word2[i]:
            prefix_match += 1
    prefix_score = prefix_match / 3
    
    return (jaccard * 0.4 + len_score * 0.3 + prefix_score * 0.3)


def search_star_patterns(words):
    found = []
    for word in words:
        w = word.lower()
        for star, patterns in STAR_PATTERNS.items():
            for pat in patterns:
                if pat in w:
                    found.append({"word": word, "star": star, "pattern": pat, "info": STAR_NAMES[star]})
                    break
    return found


def get_botanical_words():
    botanical_text = vd.get_section_text("herbal_a")
    words = set()
    for page in botanical_text.values():
        for text in page.values():
            words.update(extract_words(text))
    return words


def get_recipes_words():
    recipes_text = vd.get_section_text("recipes")
    words = set()
    for page in recipes_text.values():
        for text in page.values():
            words.update(extract_words(text))
    return words


def main():
    print("Track 63: Astronomical Section Validation")
    print("=" * 50)
    
    dictionary = load_dictionary()
    print(f"Loaded dictionary: {len(dictionary)} entries")
    
    zodiac_data = get_zodiac_text()
    print(f"Loaded zodiac folios: {len(zodiac_data)}")
    
    results = {
        "folios_analyzed": [],
        "coverage_rate": 0,
        "zodiac_labels": {},
        "star_matches": [],
        "new_vocabulary": [],
        "cross_section_comparison": {},
        "folio_details": {}
    }
    
    all_astro_words = set()
    total_words = 0
    total_translated = 0
    
    print("\n--- Analyzing Zodiac Folios ---")
    for folio, data in zodiac_data.items():
        sign = data["sign"]
        lines = data["lines"]
        
        if not lines:
            print(f"  {folio} ({sign}): No text found")
            continue
        
        trans = translate_section(lines, dictionary)
        total_words += trans["total_words"]
        total_translated += trans["translated"]
        
        for text in lines.values():
            all_astro_words.update(extract_words(text))
        
        labels = find_label_words(lines)
        label_matches = {}
        for label in labels[:10]:
            match = match_zodiac_name(label, sign)
            if match:
                label_matches[label] = match
        
        results["folio_details"][folio] = {
            "sign": sign,
            "word_count": trans["total_words"],
            "coverage": round(trans["coverage"] * 100, 1),
            "top_words": list(trans["word_freq"].keys())[:10],
            "label_candidates": labels[:10],
            "label_matches": label_matches
        }
        
        results["folios_analyzed"].append(folio)
        
        sign_key = sign.split()[0].lower()
        if sign_key not in results["zodiac_labels"]:
            results["zodiac_labels"][sign_key] = {
                "folio": folio,
                "labels": labels[:5],
                "matches": label_matches
            }
        
        print(f"  {folio} ({sign}): {trans['total_words']} words, {trans['coverage']*100:.1f}% coverage")
    
    overall_coverage = total_translated / total_words if total_words > 0 else 0
    results["coverage_rate"] = round(overall_coverage * 100, 1)
    print(f"\nOverall coverage: {results['coverage_rate']}%")
    
    print("\n--- Searching for Star Names ---")
    star_matches = search_star_patterns(all_astro_words)
    results["star_matches"] = star_matches
    if star_matches:
        for m in star_matches[:10]:
            print(f"  Found: {m['word']} matches pattern '{m['pattern']}' for {m['star']}")
    else:
        print("  No direct star name patterns found")
    
    for star, info in STAR_NAMES.items():
        constellation = info["constellation"]
        if constellation in results["zodiac_labels"]:
            labels = results["zodiac_labels"][constellation].get("labels", [])
            for label in labels:
                for pat in STAR_PATTERNS.get(star, []):
                    if pat in label.lower():
                        results["star_matches"].append({
                            "word": label,
                            "star": star,
                            "pattern": pat,
                            "context": f"Found in {constellation} section"
                        })
    
    print("\n--- Cross-Section Analysis ---")
    botanical_words = get_botanical_words()
    recipes_words = get_recipes_words()
    
    only_in_astro = all_astro_words - botanical_words - recipes_words
    shared_with_botanical = all_astro_words & botanical_words
    shared_with_recipes = all_astro_words & recipes_words
    
    results["cross_section_comparison"] = {
        "astronomical_unique": len(only_in_astro),
        "astronomical_total": len(all_astro_words),
        "shared_with_botanical": len(shared_with_botanical),
        "shared_with_recipes": len(shared_with_recipes),
        "botanical_total": len(botanical_words),
        "recipes_total": len(recipes_words),
        "overlap_percentage": round(len(shared_with_botanical | shared_with_recipes) / len(all_astro_words) * 100, 1) if all_astro_words else 0
    }
    
    print(f"  Astronomical unique words: {len(only_in_astro)}")
    print(f"  Shared with botanical: {len(shared_with_botanical)}")
    print(f"  Shared with recipes: {len(shared_with_recipes)}")
    
    print("\n--- Finding New Vocabulary ---")
    new_vocab_candidates = []
    for word in sorted(only_in_astro, key=lambda x: -len(x))[:100]:
        if len(word) > 3 and word not in dictionary:
            matches = {}
            for sign, info in ZODIAC_INFO.items():
                sign_score = simple_match_score(word.lower(), info["latin"])
                if sign_score > 0.4:
                    matches[f"zodiac_{sign}"] = sign_score
                month_score = simple_match_score(word.lower(), info["month_lat"])
                if month_score > 0.4:
                    matches[f"month_{info['month_lat']}"] = month_score
            
            if matches or len(word) >= 5:
                new_vocab_candidates.append({
                    "word": word,
                    "length": len(word),
                    "potential_matches": matches
                })
    
    results["new_vocabulary"] = new_vocab_candidates[:50]
    print(f"  Found {len(new_vocab_candidates)} potential new vocabulary items")
    
    if new_vocab_candidates:
        print("  Top candidates:")
        for item in new_vocab_candidates[:5]:
            if item["potential_matches"]:
                print(f"    {item['word']}: {item['potential_matches']}")
    
    with open(OUTPUT_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {OUTPUT_JSON}")
    
    generate_report(results, dictionary)
    print(f"Saved: {OUTPUT_MD}")


def generate_report(results, dictionary):
    lines = [
        "# Track 63: Astronomical Section Validation Report",
        "",
        "## Executive Summary",
        "",
        f"- **Folios analyzed**: {len(results['folios_analyzed'])}",
        f"- **Overall coverage**: {results['coverage_rate']}%",
        f"- **Star pattern matches**: {len(results['star_matches'])}",
        f"- **New vocabulary candidates**: {len(results['new_vocabulary'])}",
        "",
        "## Coverage Comparison",
        "",
        "| Section | Coverage |",
        "|---------|----------|",
        f"| **Astronomical** | **{results['coverage_rate']}%** |",
        "| Botanical (from Track 57) | 83.3% (illustration) |",
        "| Recipes (from Track 59) | 38.9% |",
        "",
    ]
    
    verdict = "POSITIVE" if results["coverage_rate"] > 30 else "WEAK"
    if results["coverage_rate"] > 40:
        verdict = "STRONG"
    
    lines.extend([
        f"**Verdict**: Dictionary performs **{verdict}** on astronomical section",
        "",
        "## Folio-by-Folio Analysis",
        "",
        "| Folio | Sign | Words | Coverage | Top Words |",
        "|-------|------|-------|----------|-----------|",
    ])
    
    for folio, details in results["folio_details"].items():
        top = ", ".join(details["top_words"][:5])
        lines.append(f"| {folio} | {details['sign']} | {details['word_count']} | {details['coverage']}% | {top} |")
    
    lines.extend([
        "",
        "## Zodiac Label Analysis",
        "",
        "Looking for matches between labels and zodiac sign/month names:",
        "",
    ])
    
    for sign, data in results["zodiac_labels"].items():
        lines.append(f"### {sign.capitalize()}")
        lines.append(f"- Labels found: {', '.join(data['labels'][:5])}")
        if data["matches"]:
            for label, matches in data["matches"].items():
                for match_type, match_info in matches.items():
                    lines.append(f"- **{label}** → {match_type}: {match_info['name']} (score: {match_info['score']:.2f})")
        lines.append("")
    
    lines.extend([
        "## Star Name Search",
        "",
    ])
    
    if results["star_matches"]:
        lines.append("| Word | Star | Pattern | Context |")
        lines.append("|------|------|---------|---------|")
        for m in results["star_matches"][:10]:
            ctx = m.get("context", m.get("info", {}).get("constellation", ""))
            lines.append(f"| {m['word']} | {m['star']} | {m['pattern']} | {ctx} |")
    else:
        lines.append("No direct star name patterns found in astronomical section.")
        lines.append("")
        lines.append("Note: Previous analysis (Track 13) found Antares pattern in Scorpio section.")
    
    lines.extend([
        "",
        "## Cross-Section Comparison",
        "",
        "| Metric | Astronomical | Botanical | Recipes |",
        "|--------|-------------|-----------|---------|",
        f"| Unique words | {results['cross_section_comparison']['astronomical_unique']} | - | - |",
        f"| Total words | {results['cross_section_comparison']['astronomical_total']} | {results['cross_section_comparison']['botanical_total']} | {results['cross_section_comparison']['recipes_total']} |",
        f"| Shared with astro | - | {results['cross_section_comparison']['shared_with_botanical']} | {results['cross_section_comparison']['shared_with_recipes']} |",
        "",
        f"**Vocabulary Overlap**: {results['cross_section_comparison']['overlap_percentage']}% of astronomical vocabulary appears in other sections",
        "",
    ])
    
    lines.extend([
        "## New Vocabulary Candidates",
        "",
        "Words unique to astronomical section that may have astronomical meanings:",
        "",
    ])
    
    if results["new_vocabulary"]:
        for item in results["new_vocabulary"][:15]:
            matches_str = ", ".join([f"{k}: {v:.2f}" for k, v in item["potential_matches"].items()]) if item["potential_matches"] else "no clear match"
            lines.append(f"- **{item['word']}** (len={item['length']}): {matches_str}")
    
    lines.extend([
        "",
        "## Key Findings",
        "",
    ])
    
    if results["coverage_rate"] >= 35:
        lines.append("1. ✅ **Dictionary works across sections** - coverage comparable to recipes section")
    else:
        lines.append("1. ⚠️ **Lower coverage than expected** - may indicate different vocabulary in astronomical section")
    
    if results["star_matches"]:
        lines.append("2. ✅ **Star name patterns found** - supports astronomical content interpretation")
    else:
        lines.append("2. ⚠️ **No clear star names** - labels may serve different purpose than naming")
    
    overlap = results["cross_section_comparison"]["overlap_percentage"]
    if overlap > 50:
        lines.append(f"3. ✅ **High vocabulary overlap ({overlap}%)** - suggests unified language across manuscript")
    else:
        lines.append(f"3. ⚠️ **Low vocabulary overlap ({overlap}%)** - astronomical section may use specialized terms")
    
    lines.extend([
        "",
        "## Implications for Hebrew Hypothesis",
        "",
        "The astronomical section provides a unique test because:",
        "",
        "1. **Zodiac signs have known Hebrew equivalents** (טלה=Aries, שור=Taurus, etc.)",
        "2. **Month names differ between Hebrew and Latin calendars**",
        "3. **Star names often derive from Arabic/Hebrew sources**",
        "",
    ])
    
    hebrew_indicators = []
    for sign, data in results["zodiac_labels"].items():
        if data["matches"]:
            for label, matches in data["matches"].items():
                if "hebrew_trans" in matches:
                    hebrew_indicators.append(f"{label} → {matches['hebrew_trans']['name']}")
    
    if hebrew_indicators:
        lines.append("**Hebrew matches found:**")
        for h in hebrew_indicators[:5]:
            lines.append(f"- {h}")
    else:
        lines.append("**No clear Hebrew zodiac name matches in labels** - labels may encode different information")
    
    lines.extend([
        "",
        "## Conclusion",
        "",
    ])
    
    if results["coverage_rate"] >= 35:
        lines.append("The clean dictionary developed from botanical/recipes sections **transfers reasonably well** to the astronomical section, suggesting a unified writing system across the manuscript.")
    else:
        lines.append("The astronomical section shows **distinct vocabulary patterns** that warrant further specialized analysis.")
    
    lines.extend([
        "",
        "---",
        f"*Generated by Track 63: Astronomical Validation*",
    ])
    
    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
