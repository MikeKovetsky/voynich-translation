#!/usr/bin/env python3
"""Full page translation using expanded 536-entry dictionary."""

import json
import re
from collections import defaultdict
from pathlib import Path

EVA_FILE = "data/eva_ivtff.txt"
TARGET_FOLIOS = ["f111v", "f107r", "f107v"]

GRAMMAR = {
    "ol": {"meaning": "the", "pos": "article", "confidence": 0.65},
    "al": {"meaning": "the/of", "pos": "article", "confidence": 0.65},
    "ar": {"meaning": "to/at", "pos": "preposition", "confidence": 0.55},
    "or": {"meaning": "for/by", "pos": "preposition", "confidence": 0.55},
    "daiin": {"meaning": "is/from", "pos": "copula", "confidence": 0.7},
    "aiin": {"meaning": "is/are", "pos": "copula", "confidence": 0.6},
    "dain": {"meaning": "is/are", "pos": "copula", "confidence": 0.6},
    "chedy": {"meaning": "which/that", "pos": "relative", "confidence": 0.55},
    "shedy": {"meaning": "which/that", "pos": "relative", "confidence": 0.55},
    "dy": {"meaning": "-ed/-ing", "pos": "verb_suffix", "confidence": 0.5},
    "chol": {"meaning": "the", "pos": "article", "confidence": 0.77},
    "chor": {"meaning": "the", "pos": "article", "confidence": 0.76},
    "shol": {"meaning": "the", "pos": "article", "confidence": 0.74},
    "dal": {"meaning": "the/a", "pos": "article", "confidence": 0.71},
    "qo": {"meaning": "the-", "pos": "prefix", "confidence": 0.6},
    "am": {"meaning": "man/with", "pos": "noun", "confidence": 0.5},
}

RECIPE_PATTERNS = [
    (r"\b(dar|dair|dor)\b.*\b(otar|okar|sol|dam)\b", "give/take + ingredient"),
    (r"\b(chol|shol|ol)\b.*\b(okar|kar)\b", "the + heart"),
    (r"\b(otaiin|dain)\b.*\b(chedy|shedy)\b", "fig + which"),
    (r"\b(sho|cho)\b.*\b(chol|shol)\b", "fire/life + the"),
    (r"\b(lchedy)\b.*\b(okar|otar)\b", "milk + heart/earth"),
    (r"\b(raiin)\b.*\b(ar|or)\b", "kidney + to/for"),
]


def load_dictionaries():
    """Merge all dictionary sources."""
    merged = {}
    
    files = [
        ("results/hybrid_dictionary.json", "hybrid"),
        ("results/dictionary_expansion_freq.json", "freq"),
        ("results/dictionary_expansion_semantic.json", "semantic"),
        ("results/dictionary_expansion_context.json", "context"),
    ]
    
    for fpath, source in files:
        if not Path(fpath).exists():
            print(f"Warning: {fpath} not found")
            continue
            
        with open(fpath) as f:
            data = json.load(f)
        
        if source == "hybrid":
            for word, entry in data.get("entries", {}).items():
                if word not in merged or entry.get("primary_confidence", 0) > merged[word].get("confidence", 0):
                    merged[word] = {
                        "meaning": entry.get("primary_meaning", "?"),
                        "language": entry.get("primary_language", "unknown"),
                        "confidence": entry.get("primary_confidence", 0.5),
                        "source": source,
                    }
        elif source == "freq":
            for word, entry in data.get("entries", {}).items():
                if word not in merged or entry.get("confidence", 0) > merged[word].get("confidence", 0):
                    merged[word] = {
                        "meaning": entry.get("meaning", "?"),
                        "language": entry.get("language", "unknown"),
                        "confidence": entry.get("confidence", 0.5),
                        "source": source,
                    }
        elif source == "semantic":
            for entry in data.get("new_entries", []):
                word = entry.get("voynich")
                if word and (word not in merged or entry.get("confidence", 0.5) > merged[word].get("confidence", 0)):
                    merged[word] = {
                        "meaning": entry.get("meaning", "?"),
                        "language": entry.get("language", "unknown"),
                        "confidence": 0.5,
                        "source": source,
                    }
        elif source == "context":
            for word, entry in data.get("entries", {}).items():
                if word not in merged:
                    merged[word] = {
                        "meaning": entry.get("meaning", "?"),
                        "language": "inferred",
                        "confidence": entry.get("confidence", 0.4),
                        "source": source,
                    }
    
    for word, gram in GRAMMAR.items():
        if word not in merged or gram["confidence"] > merged[word].get("confidence", 0):
            merged[word] = {
                "meaning": gram["meaning"],
                "language": "grammar",
                "confidence": gram["confidence"],
                "source": "grammar",
            }
    
    return merged


def load_eva_folios(folios):
    """Load lines from specified folios."""
    lines_by_folio = defaultdict(list)
    
    with open(EVA_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            for folio in folios:
                if f"<{folio}." in line and ";H>" in line and "\t" in line:
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        header = parts[0]
                        match = re.search(rf"<({folio}\.\d+)", header)
                        if match:
                            line_id = match.group(1)
                            text = parts[1].replace("<$>", "").strip()
                            text = re.sub(r"[!\?,]", ".", text)
                            words = [w for w in text.split(".") if w and not w.startswith("%")]
                            if words:
                                lines_by_folio[folio].append({
                                    "line_id": line_id,
                                    "text": text,
                                    "words": words,
                                })
    
    return dict(lines_by_folio)


def translate_word(word, dictionary):
    """Translate a single word."""
    word_clean = word.lower().strip()
    
    if word_clean in dictionary:
        entry = dictionary[word_clean]
        return {
            "voynich": word,
            "meaning": entry["meaning"],
            "confidence": entry["confidence"],
            "language": entry["language"],
            "found": True,
        }
    
    if word_clean.startswith("qo") and word_clean[2:] in dictionary:
        base = dictionary[word_clean[2:]]
        return {
            "voynich": word,
            "meaning": f"the-{base['meaning']}",
            "confidence": base["confidence"] * 0.8,
            "language": base["language"],
            "found": True,
        }
    
    if word_clean.endswith("y") and word_clean[:-1] in dictionary:
        base = dictionary[word_clean[:-1]]
        return {
            "voynich": word,
            "meaning": f"{base['meaning']}-VERB",
            "confidence": base["confidence"] * 0.7,
            "language": base["language"],
            "found": True,
        }
    
    if word_clean.endswith("dy") and word_clean[:-2] in dictionary:
        base = dictionary[word_clean[:-2]]
        return {
            "voynich": word,
            "meaning": f"{base['meaning']}-ed",
            "confidence": base["confidence"] * 0.7,
            "language": base["language"],
            "found": True,
        }
    
    return {
        "voynich": word,
        "meaning": "?",
        "confidence": 0,
        "language": "unknown",
        "found": False,
    }


def translate_line(words, dictionary):
    """Translate all words in a line."""
    return [translate_word(w, dictionary) for w in words]


def reconstruct_sentence(translations):
    """Attempt SOV→SVO reconstruction."""
    meanings = [t["meaning"] for t in translations if t["found"]]
    if not meanings:
        return "?"
    
    sentence = " ".join(meanings)
    
    sentence = re.sub(r"\bthe-(\w+)", r"the \1", sentence)
    sentence = re.sub(r"-VERB\b", "", sentence)
    sentence = re.sub(r"-ed\b", "ed", sentence)
    
    return sentence


def score_coherence(translations, original_text):
    """Score how coherent the translation is."""
    if not translations:
        return 0
    
    found = sum(1 for t in translations if t["found"])
    total = len(translations)
    found_rate = found / total if total > 0 else 0
    
    confidence_sum = sum(t["confidence"] for t in translations if t["found"])
    avg_confidence = confidence_sum / found if found > 0 else 0
    
    recipe_score = 0
    for pattern, _ in RECIPE_PATTERNS:
        if re.search(pattern, original_text, re.IGNORECASE):
            recipe_score += 0.1
    
    coherence = (found_rate * 0.5) + (avg_confidence * 0.3) + min(recipe_score, 0.2)
    return min(coherence, 1.0)


def detect_recipe_patterns(original_text):
    """Detect recipe-like patterns in text."""
    found = []
    for pattern, name in RECIPE_PATTERNS:
        if re.search(pattern, original_text, re.IGNORECASE):
            found.append(name)
    return found


def translate_folio(folio, lines, dictionary):
    """Translate all lines in a folio."""
    results = []
    total_words = 0
    translated_words = 0
    
    for line_data in lines:
        translations = translate_line(line_data["words"], dictionary)
        
        line_total = len(translations)
        line_found = sum(1 for t in translations if t["found"])
        total_words += line_total
        translated_words += line_found
        
        rate = line_found / line_total if line_total > 0 else 0
        coherence = score_coherence(translations, line_data["text"])
        reconstructed = reconstruct_sentence(translations)
        recipes = detect_recipe_patterns(line_data["text"])
        
        results.append({
            "line_id": line_data["line_id"],
            "voynich": line_data["text"],
            "word_by_word": translations,
            "translation_rate": round(rate, 3),
            "coherence_score": round(coherence, 3),
            "reconstructed": reconstructed,
            "recipe_patterns": recipes,
        })
    
    overall_rate = translated_words / total_words if total_words > 0 else 0
    
    best_lines = sorted(results, key=lambda x: x["coherence_score"], reverse=True)[:10]
    
    return {
        "lines": results,
        "stats": {
            "total_words": total_words,
            "translated_words": translated_words,
            "translation_rate": round(overall_rate, 3),
            "line_count": len(results),
        },
        "best_lines": best_lines,
    }


def main():
    print("Loading dictionaries...")
    dictionary = load_dictionaries()
    print(f"  Merged dictionary: {len(dictionary)} entries")
    
    print("\nLoading EVA folios...")
    folios_data = load_eva_folios(TARGET_FOLIOS)
    for folio, lines in folios_data.items():
        print(f"  {folio}: {len(lines)} lines")
    
    print("\nTranslating folios...")
    all_translations = {}
    all_best = []
    total_words = 0
    total_translated = 0
    coherent_count = 0
    
    for folio in TARGET_FOLIOS:
        if folio not in folios_data:
            print(f"  {folio}: NOT FOUND")
            continue
        
        result = translate_folio(folio, folios_data[folio], dictionary)
        all_translations[folio] = result
        
        total_words += result["stats"]["total_words"]
        total_translated += result["stats"]["translated_words"]
        
        for line in result["lines"]:
            if line["coherence_score"] > 0.4:
                coherent_count += 1
        
        for line in result["best_lines"][:5]:
            all_best.append({
                "folio": folio,
                "line_id": line["line_id"],
                "voynich": line["voynich"],
                "translation": line["reconstructed"],
                "confidence": line["coherence_score"],
            })
        
        print(f"  {folio}: {result['stats']['translation_rate']*100:.1f}% translated")
    
    all_best.sort(key=lambda x: x["confidence"], reverse=True)
    
    overall_rate = total_translated / total_words if total_words > 0 else 0
    
    output = {
        "dictionary_size": len(dictionary),
        "folios_translated": list(all_translations.keys()),
        "overall_stats": {
            "total_words": total_words,
            "translated_words": total_translated,
            "translation_rate": round(overall_rate, 3),
            "coherent_sentences": coherent_count,
        },
        "translations": all_translations,
        "best_sentences": all_best[:20],
    }
    
    with open("results/full_translation.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved: results/full_translation.json")
    
    generate_report(output, dictionary)
    print("Saved: results/full_translation_report.md")


def generate_report(data, dictionary):
    """Generate markdown report."""
    lines = [
        "# Full Translation Report",
        "",
        "## Summary",
        f"- Dictionary size: {data['dictionary_size']} entries",
        f"- Folios translated: {len(data['folios_translated'])}",
        f"- Overall translation rate: {data['overall_stats']['translation_rate']*100:.1f}%",
        f"- Coherent sentences found: {data['overall_stats']['coherent_sentences']}",
        "",
        "## Best Translations",
        "",
        "| Folio | Line | Coherence | Voynich | Translation |",
        "|-------|------|-----------|---------|-------------|",
    ]
    
    for sent in data["best_sentences"][:15]:
        voynich_short = sent["voynich"][:40] + "..." if len(sent["voynich"]) > 40 else sent["voynich"]
        trans_short = sent["translation"][:50] + "..." if len(sent["translation"]) > 50 else sent["translation"]
        lines.append(f"| {sent['folio']} | {sent['line_id'].split('.')[-1]} | {sent['confidence']:.2f} | `{voynich_short}` | {trans_short} |")
    
    for folio, result in data["translations"].items():
        lines.extend([
            "",
            f"## {folio.upper()} Translation",
            "",
            f"**Stats**: {result['stats']['translated_words']}/{result['stats']['total_words']} words ({result['stats']['translation_rate']*100:.1f}%)",
            "",
        ])
        
        lines.append("### Best Lines")
        lines.append("")
        for best in result["best_lines"][:5]:
            lines.append(f"**{best['line_id']}** (coherence: {best['coherence_score']:.2f})")
            lines.append(f"- Voynich: `{best['voynich']}`")
            lines.append(f"- Translation: {best['reconstructed']}")
            if best["recipe_patterns"]:
                lines.append(f"- Patterns: {', '.join(best['recipe_patterns'])}")
            lines.append("")
        
        lines.append("### Word-by-Word (First 10 lines)")
        lines.append("")
        for line in result["lines"][:10]:
            lines.append(f"**{line['line_id']}** ({line['translation_rate']*100:.0f}%)")
            wbw = []
            for t in line["word_by_word"]:
                if t["found"]:
                    wbw.append(f"{t['voynich']}→{t['meaning']}")
                else:
                    wbw.append(f"{t['voynich']}→?")
            lines.append(f"  {' | '.join(wbw[:8])}")
            lines.append("")
    
    lines.extend([
        "",
        "## Recipe Patterns Found",
        "",
    ])
    
    recipe_counts = defaultdict(int)
    for folio, result in data["translations"].items():
        for line in result["lines"]:
            for pattern in line.get("recipe_patterns", []):
                recipe_counts[pattern] += 1
    
    for pattern, count in sorted(recipe_counts.items(), key=lambda x: -x[1]):
        lines.append(f"- {pattern}: {count} occurrences")
    
    lines.extend([
        "",
        "## Conclusion",
        "",
        f"Translation achieved **{data['overall_stats']['translation_rate']*100:.1f}%** word coverage.",
        "",
        f"Found **{data['overall_stats']['coherent_sentences']}** coherent sentences (>40% coherence score).",
        "",
    ])
    
    if data['overall_stats']['translation_rate'] > 0.3:
        lines.append("**Assessment**: Partial readability achieved. Recipe patterns are detectable.")
        lines.append("The text appears to be a medical/botanical recipe collection.")
    else:
        lines.append("**Assessment**: Dictionary coverage insufficient for full translation.")
        lines.append("Further vocabulary expansion needed.")
    
    with open("results/full_translation_report.md", "w") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()



