import json
import re
from collections import defaultdict, Counter

EVA_FILE = "data/eva_ivtff.txt"
DICT_FILE = "results/master_dictionary.json"

TARGET_FOLIOS = {
    "f9v": {
        "expert_id": "viola tricolor (pansy)",
        "confidence": "HIGH",
        "expected_vocab": {
            "plant_name": ["viola", "segel", "pansy", "tricolor"],
            "flower": ["flower", "petal", "perach", "bloom"],
            "color": ["purple", "yellow", "blue", "white"],
            "leaf": ["leaf", "aleh", "heart-shaped"],
            "root": ["root", "shoresh", "shor"],
            "medicinal": ["heart", "skin", "asthma", "epilepsy", "emetic"]
        },
        "hebrew_names": ["סגל", "פרח", "עלה", "שורש"]
    },
    "f51r": {
        "expert_id": "ricinus communis (castor oil)",
        "confidence": "HIGH",
        "expected_vocab": {
            "plant_name": ["ricinus", "castor", "kikyon", "oil_plant"],
            "seed": ["seed", "zera", "oil"],
            "leaf": ["leaf", "aleh", "star", "seven-pointed"],
            "fruit": ["fruit", "spiky", "capsule"],
            "medicinal": ["oil", "shemen", "purgative", "laxative"]
        },
        "hebrew_names": ["קיקיון", "שמן", "זרע"]
    },
    "f6v": {
        "expert_id": "ricinus communis (castor oil)",
        "confidence": "HIGH",
        "expected_vocab": {
            "plant_name": ["ricinus", "castor", "kikyon"],
            "seed": ["seed", "zera", "oil"],
            "leaf": ["leaf", "star", "pointed"],
            "medicinal": ["oil", "shemen", "purgative"]
        },
        "hebrew_names": ["קיקיון", "שמן"]
    },
    "f16r": {
        "expert_id": "cannabis sativa (hemp)",
        "confidence": "HIGH",
        "expected_vocab": {
            "plant_name": ["cannabis", "hemp", "kanabos", "canapa"],
            "leaf": ["leaf", "star", "serrated", "pointed"],
            "seed": ["seed", "zera"],
            "fiber": ["fiber", "rope", "textile"],
            "medicinal": ["pain", "sleep", "sedative"]
        },
        "hebrew_names": ["קנאביס", "קנבוס"]
    },
    "f7r": {
        "expert_id": "nymphaea alba (water lily) / paeonia",
        "confidence": "MEDIUM",
        "expected_vocab": {
            "plant_name": ["nymphaea", "lily", "water", "peony", "paeonia"],
            "flower": ["flower", "perach", "petal", "white"],
            "root": ["root", "shoresh", "rhizome"],
            "water": ["water", "mayim", "pond", "lake"],
            "medicinal": ["sedative", "pain", "inflammation"]
        },
        "hebrew_names": ["שושן", "מים", "פרח"]
    }
}


def load_dictionary():
    with open(DICT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get("entries", {})


def extract_folio_words(folio_id):
    words = []
    in_folio = False
    pattern = re.compile(rf'^<{folio_id}\.(\d+)[^;]*;H>\t(.+)$')
    
    with open(EVA_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith(f'<{folio_id}>'):
                in_folio = True
                continue
            if in_folio and line.startswith('<f') and not line.startswith(f'<{folio_id}'):
                break
            if in_folio:
                match = pattern.match(line)
                if match:
                    line_num = match.group(1)
                    text = match.group(2)
                    text = re.sub(r'<[^>]+>', '', text)
                    text = re.sub(r'[!.,]', '.', text)
                    line_words = [w.strip() for w in text.split('.') if w.strip()]
                    for i, w in enumerate(line_words):
                        words.append({
                            "position": f"L{line_num}.W{i+1}",
                            "word": w
                        })
    return words


def translate_word(word, dictionary):
    if word in dictionary:
        entry = dictionary[word]
        return {
            "translation": entry.get("meaning", "?"),
            "language": entry.get("language", "unknown"),
            "confidence": entry.get("confidence", 0),
            "domain": entry.get("domain", "unknown")
        }
    return None


def check_expected_match(translation, expected_vocab):
    if not translation:
        return None
    meaning = translation["translation"].lower()
    for category, terms in expected_vocab.items():
        for term in terms:
            if term.lower() in meaning or meaning in term.lower():
                return {"category": category, "term": term, "match_type": "semantic"}
    return None


def analyze_folio(folio_id, info, dictionary):
    words = extract_folio_words(folio_id)
    results = {
        "folio": folio_id,
        "expert_id": info["expert_id"],
        "confidence": info["confidence"],
        "total_words": len(words),
        "words": []
    }
    
    translated = 0
    correct = 0
    semantic_matches = 0
    unknown = 0
    
    domain_counts = Counter()
    language_counts = Counter()
    category_matches = Counter()
    
    for w in words:
        word = w["word"]
        trans = translate_word(word, dictionary)
        
        entry = {
            "position": w["position"],
            "word": word,
            "translation": None,
            "language": None,
            "confidence": None,
            "domain": None,
            "expected_match": None,
            "status": "unknown"
        }
        
        if trans:
            entry["translation"] = trans["translation"]
            entry["language"] = trans["language"]
            entry["confidence"] = trans["confidence"]
            entry["domain"] = trans["domain"]
            entry["status"] = "translated"
            translated += 1
            domain_counts[trans["domain"]] += 1
            language_counts[trans["language"]] += 1
            
            match = check_expected_match(trans, info["expected_vocab"])
            if match:
                entry["expected_match"] = match
                entry["status"] = "matched"
                semantic_matches += 1
                correct += 1
                category_matches[match["category"]] += 1
            else:
                if trans["domain"] in ["botanical", "medical", "grammar"]:
                    entry["status"] = "plausible"
                else:
                    entry["status"] = "unverified"
        else:
            unknown += 1
        
        results["words"].append(entry)
    
    results["metrics"] = {
        "total_words": len(words),
        "dictionary_matches": translated,
        "semantic_matches": semantic_matches,
        "coverage_rate": round(translated / len(words), 4) if words else 0,
        "semantic_match_rate": round(semantic_matches / len(words), 4) if words else 0,
        "unknown_words": unknown
    }
    
    results["domain_distribution"] = dict(domain_counts)
    results["language_distribution"] = dict(language_counts)
    results["category_matches"] = dict(category_matches)
    
    return results


def analyze_errors(results):
    errors = []
    
    for folio_result in results:
        folio = folio_result["folio"]
        expert_id = folio_result["expert_id"]
        
        for word in folio_result["words"]:
            if word["status"] == "unverified" and word["translation"]:
                errors.append({
                    "folio": folio,
                    "position": word["position"],
                    "word": word["word"],
                    "our_translation": word["translation"],
                    "expert_plant": expert_id,
                    "error_type": "semantic_mismatch",
                    "reason": f"'{word['translation']}' not related to {expert_id}"
                })
    
    return errors


def propose_corrections(results, errors, dictionary):
    corrections = []
    
    unknown_words = Counter()
    for r in results:
        for w in r["words"]:
            if w["status"] == "unknown":
                unknown_words[w["word"]] += 1
    
    for word, count in unknown_words.most_common(20):
        corrections.append({
            "type": "add_entry",
            "word": word,
            "frequency": count,
            "suggestion": "Investigate this high-frequency unknown word"
        })
    
    error_patterns = Counter()
    for e in errors:
        error_patterns[e["our_translation"]] += 1
    
    for trans, count in error_patterns.most_common(10):
        if count >= 2:
            corrections.append({
                "type": "review_entry",
                "current_translation": trans,
                "occurrence_count": count,
                "reason": "Translation appears incorrect in multiple botanical contexts"
            })
    
    return corrections


def generate_report(results, errors, corrections):
    lines = [
        "# Track 77: Deep Word-by-Word Validation Report",
        "",
        "## Overview",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
    ]
    
    total_words = sum(r["metrics"]["total_words"] for r in results)
    total_covered = sum(r["metrics"]["dictionary_matches"] for r in results)
    total_semantic = sum(r["metrics"]["semantic_matches"] for r in results)
    
    lines.append(f"| Folios Tested | {len(results)} |")
    lines.append(f"| Total Words | {total_words} |")
    lines.append(f"| Dictionary Coverage | {total_covered} ({round(100*total_covered/total_words, 1)}%) |")
    lines.append(f"| Semantic Matches | {total_semantic} ({round(100*total_semantic/total_words, 1)}%) |")
    lines.append(f"| Unknown Words | {total_words - total_covered} |")
    lines.append("")
    
    lines.append("## Per-Folio Results")
    lines.append("")
    lines.append("| Folio | Expert ID | Words | Coverage | Semantic |")
    lines.append("|-------|-----------|-------|----------|----------|")
    
    for r in results:
        m = r["metrics"]
        lines.append(f"| {r['folio']} | {r['expert_id'][:30]} | {m['total_words']} | {round(100*m['coverage_rate'], 1)}% | {round(100*m['semantic_match_rate'], 1)}% |")
    
    lines.append("")
    lines.append("## Word-by-Word Breakdown")
    lines.append("")
    
    for r in results:
        lines.append(f"### {r['folio']} - {r['expert_id']}")
        lines.append("")
        lines.append("| Position | Voynich | Translation | Domain | Status |")
        lines.append("|----------|---------|-------------|--------|--------|")
        
        for w in r["words"][:30]:
            trans = w["translation"] or "?"
            domain = w["domain"] or "-"
            status = w["status"]
            status_icon = {"matched": "✅", "plausible": "⚠️", "translated": "📝", "unknown": "❓", "unverified": "❌"}.get(status, "?")
            lines.append(f"| {w['position']} | {w['word']} | {trans} | {domain} | {status_icon} {status} |")
        
        if len(r["words"]) > 30:
            lines.append(f"| ... | ({len(r['words']) - 30} more words) | ... | ... | ... |")
        
        lines.append("")
        lines.append(f"**Domain Distribution**: {r['domain_distribution']}")
        lines.append(f"**Language Distribution**: {r['language_distribution']}")
        lines.append(f"**Category Matches**: {r['category_matches']}")
        lines.append("")
    
    lines.append("## Error Analysis")
    lines.append("")
    if errors:
        lines.append("| Folio | Word | Our Translation | Expert Plant | Error Type |")
        lines.append("|-------|------|-----------------|--------------|------------|")
        for e in errors[:20]:
            lines.append(f"| {e['folio']} | {e['word']} | {e['our_translation']} | {e['expert_plant'][:25]} | {e['error_type']} |")
        lines.append("")
    else:
        lines.append("No systematic errors detected.")
        lines.append("")
    
    lines.append("## Proposed Corrections")
    lines.append("")
    
    add_entries = [c for c in corrections if c["type"] == "add_entry"]
    if add_entries:
        lines.append("### High-Frequency Unknown Words (Potential New Entries)")
        lines.append("")
        lines.append("| Word | Frequency | Suggestion |")
        lines.append("|------|-----------|------------|")
        for c in add_entries[:15]:
            lines.append(f"| {c['word']} | {c['frequency']} | {c['suggestion']} |")
        lines.append("")
    
    review_entries = [c for c in corrections if c["type"] == "review_entry"]
    if review_entries:
        lines.append("### Translations Needing Review")
        lines.append("")
        lines.append("| Current Translation | Occurrences | Reason |")
        lines.append("|---------------------|-------------|--------|")
        for c in review_entries:
            lines.append(f"| {c['current_translation']} | {c['occurrence_count']} | {c['reason'][:40]} |")
        lines.append("")
    
    lines.append("## Validation Assessment")
    lines.append("")
    
    overall_coverage = total_covered / total_words if total_words else 0
    semantic_rate = total_semantic / total_words if total_words else 0
    
    if semantic_rate >= 0.15:
        assessment = "STRONG"
        desc = "Significant semantic alignment between translations and expert plant IDs"
    elif semantic_rate >= 0.05:
        assessment = "MODERATE"
        desc = "Some semantic alignment detected, but many unverified translations"
    else:
        assessment = "WEAK"
        desc = "Low semantic alignment - translations may not reflect plant content"
    
    lines.append(f"**Overall Assessment: {assessment}**")
    lines.append("")
    lines.append(f"- {desc}")
    lines.append(f"- Dictionary coverage: {round(100*overall_coverage, 1)}%")
    lines.append(f"- Semantic match rate: {round(100*semantic_rate, 1)}%")
    lines.append("")
    
    lines.append("## Key Findings")
    lines.append("")
    
    all_domains = Counter()
    all_languages = Counter()
    for r in results:
        all_domains.update(r["domain_distribution"])
        all_languages.update(r["language_distribution"])
    
    lines.append(f"1. **Dominant Domains**: {dict(all_domains.most_common(5))}")
    lines.append(f"2. **Language Mix**: {dict(all_languages.most_common(5))}")
    lines.append(f"3. **Errors Found**: {len(errors)}")
    lines.append(f"4. **New Words Proposed**: {len(add_entries)}")
    lines.append("")
    
    return "\n".join(lines)


def main():
    print("Loading dictionary...")
    dictionary = load_dictionary()
    print(f"Dictionary has {len(dictionary)} entries")
    
    results = []
    for folio_id, info in TARGET_FOLIOS.items():
        print(f"Analyzing {folio_id} ({info['expert_id']})...")
        result = analyze_folio(folio_id, info, dictionary)
        results.append(result)
        print(f"  - {result['metrics']['total_words']} words, {result['metrics']['coverage_rate']*100:.1f}% coverage")
    
    print("\nAnalyzing errors...")
    errors = analyze_errors(results)
    print(f"Found {len(errors)} potential errors")
    
    print("Proposing corrections...")
    corrections = propose_corrections(results, errors, dictionary)
    print(f"Proposed {len(corrections)} corrections")
    
    output_data = {
        "folios_tested": len(results),
        "total_words": sum(r["metrics"]["total_words"] for r in results),
        "accuracy": {
            "coverage": round(sum(r["metrics"]["coverage_rate"] for r in results) / len(results), 4),
            "semantic_match": round(sum(r["metrics"]["semantic_match_rate"] for r in results) / len(results), 4)
        },
        "per_folio_results": results,
        "error_analysis": errors,
        "corrections_proposed": corrections
    }
    
    with open("results/deep_validation.json", 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print("\nSaved results/deep_validation.json")
    
    report = generate_report(results, errors, corrections)
    with open("results/deep_validation_report.md", 'w', encoding='utf-8') as f:
        f.write(report)
    print("Saved results/deep_validation_report.md")
    
    print("\n" + "="*60)
    print("DEEP VALIDATION COMPLETE")
    print("="*60)
    print(f"Folios tested: {len(results)}")
    print(f"Total words: {output_data['total_words']}")
    print(f"Average coverage: {output_data['accuracy']['coverage']*100:.1f}%")
    print(f"Semantic match rate: {output_data['accuracy']['semantic_match']*100:.1f}%")


if __name__ == "__main__":
    main()



