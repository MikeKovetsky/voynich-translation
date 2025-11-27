#!/usr/bin/env python3
"""Translate botanical section using 409-entry dictionary."""

import json
import re
from collections import defaultdict
from pathlib import Path

EVA_FILE = "data/eva_ivtff.txt"

BOTANICAL_FOLIOS = [
    "f2v", "f3r", "f4r", "f5r", "f6r", 
    "f7r", "f8r", "f9r", "f10r", "f11r"
]

PLANT_PATTERNS = [
    (r"\b(radix|root|raiin)\b", "root mention"),
    (r"\b(folia|leaf|lshey|lshy)\b", "leaf mention"),
    (r"\b(flos|flower|flor)\b", "flower mention"),
    (r"\b(semen|seed|sam|sem)\b", "seed mention"),
    (r"\b(otar|tar|terra)\b", "earth/ground"),
    (r"\b(aqua|water|aqu)\b", "water mention"),
    (r"\b(chol|shol|sick)\b", "sickness/treatment"),
    (r"\b(dar|dair|give)\b", "instruction verb"),
    (r"\b(chor|kor|color)\b", "color reference"),
    (r"\b(olor|odor|smell)\b", "smell reference"),
]

BOTANICAL_VOCAB = {
    "radix": "root",
    "folia": "leaf/leaves",
    "flos": "flower",
    "semen": "seed",
    "cortex": "bark",
    "herba": "herb",
    "planta": "plant",
    "succus": "juice",
    "pulvis": "powder",
    "infusio": "infusion",
}

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
    "chol": {"meaning": "sick", "pos": "adjective", "confidence": 0.77},
    "chor": {"meaning": "the/color", "pos": "article", "confidence": 0.76},
    "shol": {"meaning": "the", "pos": "article", "confidence": 0.74},
    "dal": {"meaning": "the/a", "pos": "article", "confidence": 0.71},
    "qo": {"meaning": "the-", "pos": "prefix", "confidence": 0.6},
    "am": {"meaning": "man/with", "pos": "noun", "confidence": 0.5},
    "sho": {"meaning": "this/that", "pos": "demonstrative", "confidence": 0.55},
    "cho": {"meaning": "this/that", "pos": "demonstrative", "confidence": 0.55},
}


def load_dictionaries():
    """Load and merge all dictionary sources."""
    merged = {}
    
    files = [
        ("results/hybrid_dictionary.json", "hybrid"),
        ("results/dictionary_expansion_freq.json", "freq"),
        ("results/dictionary_expansion_semantic.json", "semantic"),
        ("results/dictionary_expansion_context.json", "context"),
    ]
    
    for fpath, source in files:
        if not Path(fpath).exists():
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


def load_botanical_folios(folios):
    """Load botanical folio lines, extracting plant labels separately."""
    lines_by_folio = defaultdict(list)
    labels_by_folio = defaultdict(list)
    
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
                            text = parts[1]
                            
                            label = None
                            if "<!plant>" in text:
                                text_parts = text.split("<!plant>")
                                text = text_parts[0]
                                if len(text_parts) > 1:
                                    label = text_parts[1].replace("<$>", "").strip()
                                    label = re.sub(r"[!\?,<>\-]", "", label)
                                    if label:
                                        labels_by_folio[folio].append({
                                            "line_id": line_id,
                                            "label": label,
                                        })
                            
                            text = text.replace("<$>", "").replace("<->", " ")
                            text = re.sub(r"[!\?,<>\-]", ".", text)
                            words = [w for w in text.split(".") if w and not w.startswith("%")]
                            
                            if words:
                                lines_by_folio[folio].append({
                                    "line_id": line_id,
                                    "text": text,
                                    "words": words,
                                    "has_label": label is not None,
                                })
    
    return dict(lines_by_folio), dict(labels_by_folio)


def translate_word(word, dictionary):
    """Translate a single Voynich word."""
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


def detect_plant_patterns(text):
    """Detect botanical patterns in text."""
    found = []
    for pattern, name in PLANT_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            found.append(name)
    return found


def reconstruct_sentence(translations):
    """Attempt sentence reconstruction."""
    meanings = [t["meaning"] for t in translations if t["found"]]
    if not meanings:
        return "?"
    
    sentence = " ".join(meanings)
    sentence = re.sub(r"\bthe-(\w+)", r"the \1", sentence)
    sentence = re.sub(r"-VERB\b", "", sentence)
    sentence = re.sub(r"-ed\b", "ed", sentence)
    
    return sentence


def translate_folio(folio, lines, dictionary):
    """Translate all lines in a folio."""
    results = []
    total_words = 0
    translated_words = 0
    
    for line_data in lines:
        translations = [translate_word(w, dictionary) for w in line_data["words"]]
        
        line_total = len(translations)
        line_found = sum(1 for t in translations if t["found"])
        total_words += line_total
        translated_words += line_found
        
        rate = line_found / line_total if line_total > 0 else 0
        reconstructed = reconstruct_sentence(translations)
        patterns = detect_plant_patterns(line_data["text"])
        
        confidence_sum = sum(t["confidence"] for t in translations if t["found"])
        avg_conf = confidence_sum / line_found if line_found > 0 else 0
        coherence = (rate * 0.6) + (avg_conf * 0.4)
        
        results.append({
            "line_id": line_data["line_id"],
            "voynich": line_data["text"],
            "word_by_word": translations,
            "translation_rate": round(rate, 3),
            "coherence_score": round(coherence, 3),
            "reconstructed": reconstructed,
            "plant_patterns": patterns,
            "has_label": line_data.get("has_label", False),
        })
    
    overall_rate = translated_words / total_words if total_words > 0 else 0
    
    return {
        "lines": results,
        "stats": {
            "total_words": total_words,
            "translated_words": translated_words,
            "translation_rate": round(overall_rate, 3),
            "line_count": len(results),
        },
    }


def analyze_labels(labels, dictionary):
    """Analyze plant labels."""
    analyzed = []
    
    for folio, label_list in labels.items():
        for item in label_list:
            words = [w for w in item["label"].split(".") if w]
            translations = [translate_word(w, dictionary) for w in words]
            
            found = sum(1 for t in translations if t["found"])
            rate = found / len(translations) if translations else 0
            
            analyzed.append({
                "folio": folio,
                "line_id": item["line_id"],
                "label": item["label"],
                "words": words,
                "translations": translations,
                "translation_rate": round(rate, 3),
            })
    
    return analyzed


def compare_vocabulary(botanical_vocab, recipe_vocab):
    """Compare vocabulary between botanical and recipe sections."""
    botanical_set = set(botanical_vocab.keys())
    recipe_set = set(recipe_vocab.keys())
    
    shared = botanical_set & recipe_set
    botanical_only = botanical_set - recipe_set
    recipe_only = recipe_set - botanical_set
    
    return {
        "shared_words": len(shared),
        "botanical_only": len(botanical_only),
        "recipe_only": len(recipe_only),
        "overlap_percentage": round(len(shared) / len(botanical_set) * 100, 1) if botanical_set else 0,
        "shared_sample": list(shared)[:30],
        "botanical_unique_sample": list(botanical_only)[:20],
    }


def extract_vocabulary(folio_results):
    """Extract unique vocabulary from translated folios."""
    vocab = {}
    for folio, result in folio_results.items():
        for line in result["lines"]:
            for t in line["word_by_word"]:
                word = t["voynich"].lower()
                if word not in vocab:
                    vocab[word] = {
                        "count": 0,
                        "found": t["found"],
                        "meaning": t["meaning"],
                    }
                vocab[word]["count"] += 1
    return vocab


def main():
    print("=" * 60)
    print("BOTANICAL SECTION TRANSLATION")
    print("=" * 60)
    
    print("\nLoading dictionaries...")
    dictionary = load_dictionaries()
    print(f"  Dictionary size: {len(dictionary)} entries")
    
    print("\nLoading botanical folios...")
    folios_data, labels_data = load_botanical_folios(BOTANICAL_FOLIOS)
    for folio in BOTANICAL_FOLIOS:
        lines = len(folios_data.get(folio, []))
        labels = len(labels_data.get(folio, []))
        print(f"  {folio}: {lines} lines, {labels} plant labels")
    
    print("\nTranslating botanical pages...")
    all_translations = {}
    total_words = 0
    total_translated = 0
    all_patterns = defaultdict(int)
    
    for folio in BOTANICAL_FOLIOS:
        if folio not in folios_data:
            print(f"  {folio}: NOT FOUND")
            continue
        
        result = translate_folio(folio, folios_data[folio], dictionary)
        all_translations[folio] = result
        
        total_words += result["stats"]["total_words"]
        total_translated += result["stats"]["translated_words"]
        
        for line in result["lines"]:
            for pattern in line.get("plant_patterns", []):
                all_patterns[pattern] += 1
        
        print(f"  {folio}: {result['stats']['translation_rate']*100:.1f}% translated ({result['stats']['total_words']} words)")
    
    overall_rate = total_translated / total_words if total_words > 0 else 0
    print(f"\nOverall translation rate: {overall_rate*100:.1f}%")
    
    print("\nAnalyzing plant labels...")
    label_analysis = analyze_labels(labels_data, dictionary)
    label_translated = sum(1 for l in label_analysis if l["translation_rate"] > 0)
    print(f"  Labels analyzed: {len(label_analysis)}")
    print(f"  Labels with translations: {label_translated}")
    
    print("\nPlant description patterns found:")
    for pattern, count in sorted(all_patterns.items(), key=lambda x: -x[1])[:10]:
        print(f"  {pattern}: {count}")
    
    print("\nComparing vocabulary with recipe section...")
    botanical_vocab = extract_vocabulary(all_translations)
    
    try:
        with open("results/full_translation.json") as f:
            recipe_data = json.load(f)
        recipe_vocab = extract_vocabulary(recipe_data.get("translations", {}))
        comparison = compare_vocabulary(botanical_vocab, recipe_vocab)
        print(f"  Shared words: {comparison['shared_words']}")
        print(f"  Botanical-only: {comparison['botanical_only']}")
        print(f"  Recipe-only: {comparison['recipe_only']}")
        print(f"  Overlap: {comparison['overlap_percentage']}%")
    except FileNotFoundError:
        comparison = {"error": "Recipe translation file not found"}
        print("  Recipe file not found - skipping comparison")
    
    best_translations = []
    for folio, result in all_translations.items():
        for line in result["lines"]:
            if line["coherence_score"] > 0.35 and line["translation_rate"] > 0.3:
                best_translations.append({
                    "folio": folio,
                    "line_id": line["line_id"],
                    "voynich": line["voynich"],
                    "translation": line["reconstructed"],
                    "coherence": line["coherence_score"],
                    "rate": line["translation_rate"],
                    "patterns": line["plant_patterns"],
                })
    
    best_translations.sort(key=lambda x: x["coherence"], reverse=True)
    
    descriptions = []
    for item in best_translations[:30]:
        patterns = item.get("patterns", [])
        if any(p in patterns for p in ["root mention", "leaf mention", "seed mention", "earth/ground"]):
            descriptions.append(item)
    
    output = {
        "dictionary_size": len(dictionary),
        "folios_translated": list(all_translations.keys()),
        "overall_stats": {
            "total_words": total_words,
            "translated_words": total_translated,
            "translation_rate": round(overall_rate, 3),
            "labels_analyzed": len(label_analysis),
        },
        "translations": all_translations,
        "plant_labels": label_analysis,
        "plant_patterns": dict(all_patterns),
        "best_sentences": best_translations[:20],
        "plant_descriptions": descriptions[:10],
        "cross_section_vocabulary": comparison,
    }
    
    with open("results/botanical_translation.json", "w") as f:
        json.dump(output, f, indent=2)
    print("\nSaved: results/botanical_translation.json")
    
    generate_report(output)
    print("Saved: results/botanical_translation_report.md")


def generate_report(data):
    """Generate markdown report."""
    lines = [
        "# Botanical Section Translation Report",
        "",
        "## Summary",
        f"- Dictionary size: {data['dictionary_size']} entries",
        f"- Folios translated: {len(data['folios_translated'])}",
        f"- Total words: {data['overall_stats']['total_words']}",
        f"- Translated words: {data['overall_stats']['translated_words']}",
        f"- **Translation rate: {data['overall_stats']['translation_rate']*100:.1f}%**",
        f"- Plant labels analyzed: {data['overall_stats']['labels_analyzed']}",
        "",
        "## Plant Description Patterns Found",
        "",
    ]
    
    for pattern, count in sorted(data["plant_patterns"].items(), key=lambda x: -x[1]):
        lines.append(f"- {pattern}: {count} occurrences")
    
    lines.extend([
        "",
        "## Best Translations",
        "",
        "| Folio | Line | Rate | Coherence | Translation |",
        "|-------|------|------|-----------|-------------|",
    ])
    
    for item in data["best_sentences"][:15]:
        trans = item["translation"][:60] + "..." if len(item["translation"]) > 60 else item["translation"]
        lines.append(f"| {item['folio']} | {item['line_id'].split('.')[-1]} | {item['rate']*100:.0f}% | {item['coherence']:.2f} | {trans} |")
    
    lines.extend([
        "",
        "## Plant Descriptions Detected",
        "",
    ])
    
    for item in data.get("plant_descriptions", [])[:10]:
        lines.append(f"**{item['folio']}.{item['line_id'].split('.')[-1]}** - Patterns: {', '.join(item.get('patterns', []))}")
        lines.append(f"- Voynich: `{item['voynich'][:80]}`")
        lines.append(f"- Translation: {item['translation']}")
        lines.append("")
    
    lines.extend([
        "",
        "## Plant Labels Analysis",
        "",
        "| Folio | Label | Words | Translation Rate |",
        "|-------|-------|-------|------------------|",
    ])
    
    for item in data["plant_labels"][:20]:
        label_short = item["label"][:30] + "..." if len(item["label"]) > 30 else item["label"]
        lines.append(f"| {item['folio']} | `{label_short}` | {len(item['words'])} | {item['translation_rate']*100:.0f}% |")
    
    comparison = data.get("cross_section_vocabulary", {})
    lines.extend([
        "",
        "## Cross-Section Vocabulary Comparison",
        "",
        f"- Shared words with recipe section: {comparison.get('shared_words', 'N/A')}",
        f"- Words unique to botanical: {comparison.get('botanical_only', 'N/A')}",
        f"- Words unique to recipes: {comparison.get('recipe_only', 'N/A')}",
        f"- Vocabulary overlap: {comparison.get('overlap_percentage', 'N/A')}%",
        "",
    ])
    
    if comparison.get("shared_sample"):
        lines.append("### Shared vocabulary (sample):")
        lines.append(f"`{', '.join(comparison['shared_sample'][:20])}`")
        lines.append("")
    
    if comparison.get("botanical_unique_sample"):
        lines.append("### Botanical-only vocabulary (sample):")
        lines.append(f"`{', '.join(comparison['botanical_unique_sample'][:20])}`")
        lines.append("")
    
    for folio, result in data["translations"].items():
        lines.extend([
            "",
            f"## {folio.upper()} Details",
            "",
            f"**Stats**: {result['stats']['translated_words']}/{result['stats']['total_words']} words ({result['stats']['translation_rate']*100:.1f}%)",
            "",
            "### Sample Lines",
            "",
        ])
        
        for line in result["lines"][:5]:
            lines.append(f"**{line['line_id']}** ({line['translation_rate']*100:.0f}%)")
            wbw = []
            for t in line["word_by_word"][:8]:
                if t["found"]:
                    wbw.append(f"{t['voynich']}→{t['meaning']}")
                else:
                    wbw.append(f"{t['voynich']}→?")
            lines.append(f"  {' | '.join(wbw)}")
            if line["plant_patterns"]:
                lines.append(f"  Patterns: {', '.join(line['plant_patterns'])}")
            lines.append("")
    
    overall_rate = data["overall_stats"]["translation_rate"]
    lines.extend([
        "",
        "## Conclusion",
        "",
        f"**Translation Rate**: {overall_rate*100:.1f}%",
        "",
    ])
    
    if overall_rate >= 0.4:
        lines.append("✅ SUCCESS: Botanical section shows >40% translation coverage")
        lines.append("The dictionary developed from recipe section transfers well to botanical content.")
    else:
        lines.append("⚠️ Translation rate below target (40%)")
        lines.append("Botanical section may have specialized vocabulary not in recipe section.")
    
    overlap = comparison.get("overlap_percentage", 0)
    if overlap > 50:
        lines.append(f"\n✅ HIGH VOCABULARY OVERLAP ({overlap}%): Both sections share core vocabulary")
    elif overlap > 30:
        lines.append(f"\n⚠️ MODERATE OVERLAP ({overlap}%): Sections share some vocabulary")
    else:
        lines.append(f"\n❌ LOW OVERLAP ({overlap}%): Sections use different vocabulary")
    
    with open("results/botanical_translation_report.md", "w") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()



