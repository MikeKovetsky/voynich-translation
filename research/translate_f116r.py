"""
Track 87: "Rosetta Page" Translation of Folio f116r
The most cross-validated page in the manuscript.
"""

import json
import re
from collections import defaultdict
from voynich_data import get_folio_text

DICT_FILE = "results/unified_dictionary.json"
GRAMMAR_FILE = "results/grammar_words.json"
PLANT_FILE = "results/plant_pair_validation.json"

VALIDATED_PLANTS = {
    "shtshy": {"plant": "aconitum", "confidence": "HIGH", "evidence": "f16r + f116r"},
    "ckhal": {"plant": "ricinus (castor oil)", "confidence": "ULTRA-HIGH", "evidence": "f6v + f51r + f116r"},
    "chtain": {"plant": "cannabis", "confidence": "HIGH", "evidence": "multiple recipe references"},
    "chetaiin": {"plant": "cannabis", "confidence": "HIGH", "evidence": "variant of chtain"},
    "chtaiin": {"plant": "cannabis", "confidence": "HIGH", "evidence": "variant of chtain"},
    "cthan": {"plant": "cannabis", "confidence": "MEDIUM", "evidence": "variant form"},
    "ytchey": {"plant": "herb (validated)", "confidence": "HIGH", "evidence": "f25r + f5v + f116r"},
}

GRAMMAR_MARKERS = {
    "daiin": {"function": "copula", "meaning": "is/from", "confidence": 0.75},
    "aiin": {"function": "copula", "meaning": "is/are", "confidence": 0.60},
    "ol": {"function": "article", "meaning": "the", "confidence": 0.65},
    "al": {"function": "article", "meaning": "the/to", "confidence": 0.65},
    "ar": {"function": "preposition", "meaning": "to/at", "confidence": 0.55},
    "or": {"function": "preposition", "meaning": "for/by", "confidence": 0.55},
    "dar": {"function": "preposition", "meaning": "of/from", "confidence": 0.50},
    "qol": {"function": "preposition", "meaning": "of/in", "confidence": 0.50},
    "chol": {"function": "article", "meaning": "the (all)", "confidence": 0.77},
    "shey": {"function": "verb_form", "meaning": "-ing/-ed", "confidence": 0.55},
    "chey": {"function": "verb_form", "meaning": "-ing/-ed", "confidence": 0.55},
    "qoky": {"function": "verb_form", "meaning": "take/do", "confidence": 0.71},
    "cthy": {"function": "verb_form", "meaning": "-ed", "confidence": 0.75},
    "oty": {"function": "verb_form", "meaning": "-ed", "confidence": 0.50},
    "dy": {"function": "suffix", "meaning": "-ly/-ed", "confidence": 0.50},
}


def load_dictionary():
    with open(DICT_FILE) as f:
        data = json.load(f)
    return data.get("entries", {})


def load_plant_pairs():
    try:
        with open(PLANT_FILE) as f:
            data = json.load(f)
        plants = {}
        for item in data.get("ultra_high_confidence", []):
            word = item["word"]
            plant = item.get("plant", "unknown plant")
            if word not in plants:
                plants[word] = {"plant": plant, "confidence": "ULTRA-HIGH"}
        for item in data.get("very_high_confidence", []):
            word = item["word"]
            plant = item.get("plant", "unknown plant")
            if word not in plants:
                plants[word] = {"plant": plant, "confidence": "VERY-HIGH"}
        return plants
    except:
        return {}


def get_f116r_text():
    folio_data = get_folio_text("f116r", "EVA", "H")
    lines = []
    for loc, text in sorted(folio_data.items()):
        m = re.match(r"f116r\.(\d+)", loc)
        if m:
            line_num = int(m.group(1))
            clean = re.sub(r"[!?<>@$]", "", text)
            words = [w for w in re.split(r"[.\-=,\s]", clean) if w and len(w) > 1]
            lines.append({"line": line_num, "raw": text, "words": words})
    return sorted(lines, key=lambda x: x["line"])


def translate_word(word, dictionary, plants, mined_plants):
    word_low = word.lower()
    
    if word_low in VALIDATED_PLANTS:
        p = VALIDATED_PLANTS[word_low]
        return f"[{p['plant'].upper()}]", "plant", p["confidence"]
    
    if word_low in mined_plants:
        p = mined_plants[word_low]
        return f"[{p['plant']}]", "plant", p["confidence"]
    
    if word_low in plants:
        p = plants[word_low]
        return f"[{p['plant']}]", "plant", p.get("confidence", "MEDIUM")
    
    if word_low in GRAMMAR_MARKERS:
        g = GRAMMAR_MARKERS[word_low]
        return f"({g['meaning']})", "grammar", g["confidence"]
    
    if word_low in dictionary:
        entry = dictionary[word_low]
        meaning = entry.get("meaning", "?")
        conf = entry.get("confidence", 0.5)
        return meaning, "vocab", conf
    
    base = re.sub(r"(aiin|ain|dy|y)$", "", word_low)
    if base and base in dictionary:
        entry = dictionary[base]
        meaning = entry.get("meaning", "?")
        return f"{meaning}+", "vocab", entry.get("confidence", 0.4)
    
    if word_low.startswith("qok") or word_low.startswith("ok"):
        return "[HERB?]", "guess", 0.3
    
    if word_low.endswith("am") or word_low.endswith("om"):
        return "[NOUN?]", "guess", 0.2
    
    return "???", "unknown", 0.0


def translate_line(line_data, dictionary, plants, mined_plants):
    translations = []
    stats = {"total": 0, "known": 0, "plant": 0, "grammar": 0, "vocab": 0, "unknown": 0}
    
    for word in line_data["words"]:
        stats["total"] += 1
        meaning, category, conf = translate_word(word, dictionary, plants, mined_plants)
        translations.append({
            "voynich": word,
            "meaning": meaning,
            "category": category,
            "confidence": conf
        })
        if category == "unknown":
            stats["unknown"] += 1
        elif category == "plant":
            stats["known"] += 1
            stats["plant"] += 1
        elif category == "grammar":
            stats["known"] += 1
            stats["grammar"] += 1
        elif category == "vocab":
            stats["known"] += 1
            stats["vocab"] += 1
        elif category == "guess":
            pass
    
    return translations, stats


def format_translation(translations):
    parts = []
    for t in translations:
        if t["category"] == "unknown":
            parts.append(f"_{t['voynich']}_")
        elif t["category"] == "guess":
            parts.append(f"~{t['meaning']}~")
        else:
            parts.append(t["meaning"])
    return " ".join(parts)


def evaluate_coherence(translations):
    if len(translations) < 3:
        return 0.0
    
    score = 0
    has_plant = any(t["category"] == "plant" for t in translations)
    has_verb = any("verb" in GRAMMAR_MARKERS.get(t["voynich"], {}).get("function", "") for t in translations)
    has_grammar = any(t["category"] == "grammar" for t in translations)
    has_noun = any(t["category"] == "vocab" for t in translations)
    
    if has_plant:
        score += 0.3
    if has_verb:
        score += 0.2
    if has_grammar:
        score += 0.2
    if has_noun:
        score += 0.2
    
    known_rate = sum(1 for t in translations if t["category"] != "unknown") / len(translations)
    score += known_rate * 0.1
    
    return min(score, 1.0)


def main():
    print("=" * 70)
    print("TRACK 87: ROSETTA PAGE TRANSLATION - FOLIO f116r")
    print("=" * 70)
    
    dictionary = load_dictionary()
    print(f"\nLoaded dictionary: {len(dictionary)} entries")
    
    mined_plants = load_plant_pairs()
    print(f"Loaded mined plants: {len(mined_plants)} entries")
    print(f"Validated plants for f116r: {len(VALIDATED_PLANTS)}")
    
    lines = get_f116r_text()
    print(f"\nFolio f116r: {len(lines)} lines")
    
    results = []
    total_stats = {"total": 0, "known": 0, "plant": 0, "grammar": 0, "vocab": 0, "unknown": 0}
    
    print("\n" + "=" * 70)
    print("LINE-BY-LINE TRANSLATION")
    print("=" * 70)
    
    for line_data in lines:
        translations, stats = translate_line(line_data, dictionary, {}, mined_plants)
        formatted = format_translation(translations)
        coherence = evaluate_coherence(translations)
        
        for k in total_stats:
            total_stats[k] += stats[k]
        
        result = {
            "line": line_data["line"],
            "voynich": " ".join(line_data["words"]),
            "translation": formatted,
            "word_translations": translations,
            "stats": stats,
            "coherence": coherence,
            "coverage": stats["known"] / stats["total"] if stats["total"] > 0 else 0
        }
        results.append(result)
        
        coverage_pct = (stats["known"] / stats["total"] * 100) if stats["total"] > 0 else 0
        
        print(f"\n[Line {line_data['line']:02d}] Coverage: {coverage_pct:.0f}% | Coherence: {coherence:.2f}")
        print(f"  VOY: {result['voynich'][:70]}...")
        print(f"  ENG: {formatted[:70]}...")
    
    print("\n" + "=" * 70)
    print("STATISTICS")
    print("=" * 70)
    
    coverage = total_stats["known"] / total_stats["total"] * 100 if total_stats["total"] > 0 else 0
    avg_coherence = sum(r["coherence"] for r in results) / len(results) if results else 0
    
    print(f"\nTotal words: {total_stats['total']}")
    print(f"Known words: {total_stats['known']} ({coverage:.1f}%)")
    print(f"  - Plants: {total_stats['plant']}")
    print(f"  - Grammar: {total_stats['grammar']}")
    print(f"  - Vocabulary: {total_stats['vocab']}")
    print(f"Unknown: {total_stats['unknown']} ({total_stats['unknown']/total_stats['total']*100:.1f}%)")
    print(f"\nAverage coherence: {avg_coherence:.2f}")
    
    high_coherence = [r for r in results if r["coherence"] >= 0.5]
    print(f"High-coherence lines (≥0.5): {len(high_coherence)} / {len(results)}")
    
    print("\n" + "=" * 70)
    print("BEST TRANSLATED LINES (Highest Coverage)")
    print("=" * 70)
    
    best = sorted(results, key=lambda x: x["coverage"], reverse=True)[:10]
    for r in best:
        print(f"\n[Line {r['line']:02d}] {r['coverage']*100:.0f}% coverage")
        print(f"  VOY: {r['voynich']}")
        print(f"  ENG: {r['translation']}")
    
    print("\n" + "=" * 70)
    print("PLANT REFERENCES FOUND")
    print("=" * 70)
    
    plant_lines = []
    for r in results:
        plants_in_line = [t for t in r["word_translations"] if t["category"] == "plant"]
        if plants_in_line:
            plant_lines.append({
                "line": r["line"],
                "plants": plants_in_line,
                "context": r["translation"]
            })
    
    for pl in plant_lines:
        print(f"\nLine {pl['line']}:")
        for p in pl["plants"]:
            print(f"  - {p['voynich']} → {p['meaning']} ({p['confidence']})")
        print(f"  Context: {pl['context'][:60]}...")
    
    output = {
        "folio": "f116r",
        "description": "Rosetta Page - most cross-validated recipe page",
        "total_lines": len(results),
        "statistics": {
            "total_words": total_stats["total"],
            "known_words": total_stats["known"],
            "coverage_rate": coverage / 100,
            "plant_words": total_stats["plant"],
            "grammar_words": total_stats["grammar"],
            "vocab_words": total_stats["vocab"],
            "unknown_words": total_stats["unknown"],
            "avg_coherence": avg_coherence
        },
        "validated_plants_used": list(VALIDATED_PLANTS.keys()),
        "lines": results,
        "high_coherence_lines": [r["line"] for r in high_coherence],
        "best_lines": [{"line": r["line"], "coverage": r["coverage"], "translation": r["translation"]} for r in best[:5]]
    }
    
    with open("results/f116r_translation.json", "w") as f:
        json.dump(output, f, indent=2)
    
    with open("results/f116r_translation.md", "w") as f:
        f.write("# Folio f116r - Rosetta Page Translation\n\n")
        f.write("## Summary\n\n")
        f.write(f"- **Total Lines**: {len(results)}\n")
        f.write(f"- **Total Words**: {total_stats['total']}\n")
        f.write(f"- **Coverage**: {coverage:.1f}%\n")
        f.write(f"- **Average Coherence**: {avg_coherence:.2f}\n\n")
        
        f.write("## Why f116r?\n\n")
        f.write("This page is our 'Rosetta Page' because it contains:\n")
        f.write("- `shtshy` = ACONITUM (validated across f16r + f116r)\n")
        f.write("- `ckhal` = RICINUS/castor oil (ULTRA-HIGH: f6v + f51r + f116r)\n")
        f.write("- `chetaiin` = CANNABIS (multiple recipe references)\n")
        f.write("- Dense recipe text with cross-validated vocabulary\n\n")
        
        f.write("## Validated Plant Names Found\n\n")
        for pl in plant_lines:
            f.write(f"### Line {pl['line']}\n")
            for p in pl["plants"]:
                f.write(f"- **{p['voynich']}** → {p['meaning']} (Confidence: {p['confidence']})\n")
            f.write(f"- *Context*: {pl['context']}\n\n")
        
        f.write("## Line-by-Line Translation\n\n")
        f.write("Legend: `_word_` = unknown | `~guess~` = inferred | `(grammar)` = function word\n\n")
        
        for r in results:
            f.write(f"### Line {r['line']}\n\n")
            f.write(f"**Voynich**: {r['voynich']}\n\n")
            f.write(f"**Translation**: {r['translation']}\n\n")
            f.write(f"**Coverage**: {r['coverage']*100:.0f}% | **Coherence**: {r['coherence']:.2f}\n\n")
            f.write("---\n\n")
        
        f.write("## Best Sentences (Mad-Libs Style)\n\n")
        f.write("Attempting to reconstruct recipe instructions:\n\n")
        
        for i, r in enumerate(best[:5], 1):
            f.write(f"{i}. **Line {r['line']}** ({r['coverage']*100:.0f}% coverage):\n")
            f.write(f"   - {r['translation']}\n\n")
        
        f.write("## Readability Assessment\n\n")
        if coverage >= 50:
            f.write("✅ **READABLE**: Over 50% of words translated\n")
        elif coverage >= 30:
            f.write("⚠️ **PARTIAL**: 30-50% coverage - key terms visible\n")
        else:
            f.write("❌ **LOW**: Under 30% - more dictionary work needed\n")
        
        f.write(f"\n**Estimated readability score**: {coverage * avg_coherence / 100:.2f} / 1.0\n")
    
    print("\n" + "=" * 70)
    print("OUTPUT FILES")
    print("=" * 70)
    print("- results/f116r_translation.json (full data)")
    print("- results/f116r_translation.md (readable report)")
    
    return output


if __name__ == "__main__":
    main()



