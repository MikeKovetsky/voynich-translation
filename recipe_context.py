#!/usr/bin/env python3
"""Deep Recipe Context Analysis for HIGH confidence plant names from Track 79."""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HIGH_CONF_PLANTS = [
    {"voynich": "shtshy", "plant": "aconitum", "folio": "f116r", "line": 13},
    {"voynich": "ychear", "plant": "ricinus", "folio": "f111v", "line": 22},
    {"voynich": "cheeal", "plant": "ricinus", "folio": "f111v", "line": 44},
    {"voynich": "opchear", "plant": "ricinus", "folio": "f113r", "line": 37},
    {"voynich": "pair", "plant": "scabiosa", "folio": "f107r", "line": 30},
    {"voynich": "qotoy", "plant": "hypericum", "folio": "f114v", "line": 18},
    {"voynich": "opchar", "plant": "papaver", "folio": "f104r", "line": 22},
    {"voynich": "otaiir", "plant": "mentastrum", "folio": "f113v", "line": 2},
]

def load_eva():
    """Load EVA transcription and parse into folio/line structure."""
    eva_path = Path("data/eva_ivtff.txt")
    folios = defaultdict(dict)
    current_folio = None
    
    with open(eva_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            
            # Match line format: <folio.line,+P0;X> text
            m = re.match(r"<(f\d+[rv]\d?)\.([\d]+[a]?),\+?P0;([HTFGUM])>\s*(.+)", line)
            if m:
                folio = m.group(1)
                line_num = m.group(2)
                source = m.group(3)
                text = m.group(4)
                
                # Prefer source H (Hebrew), then F, then others
                key = (folio, line_num)
                if key not in folios or source == "H" or (source == "F" and folios[folio].get(line_num, {}).get("source") not in ["H"]):
                    folios[folio][line_num] = {"text": text, "source": source}
    
    return folios


def load_dict():
    """Load master dictionary."""
    dict_path = Path("results/master_dictionary.json")
    with open(dict_path, "r") as f:
        data = json.load(f)
    return data.get("entries", {})


def extract_context(folios, folio, line_num, context_lines=3):
    """Extract full line and surrounding context."""
    lines = folios.get(folio, {})
    line_nums = sorted([int(re.match(r"(\d+)", ln).group(1)) for ln in lines.keys() if re.match(r"\d+", ln)])
    
    target_idx = None
    for i, ln in enumerate(line_nums):
        if ln == line_num:
            target_idx = i
            break
    
    if target_idx is None:
        return None
    
    before = []
    after = []
    main_line = None
    
    for i, ln in enumerate(line_nums):
        line_key = str(ln)
        if line_key not in lines:
            continue
        
        if i < target_idx and i >= target_idx - context_lines:
            before.append({"line": ln, "text": lines[line_key]["text"]})
        elif i == target_idx:
            main_line = {"line": ln, "text": lines[line_key]["text"]}
        elif i > target_idx and i <= target_idx + context_lines:
            after.append({"line": ln, "text": lines[line_key]["text"]})
    
    return {
        "context_before": before,
        "main_line": main_line,
        "context_after": after
    }


def translate_line(text, dictionary, plant_word, plant_name):
    """Translate a line using the dictionary."""
    words = re.split(r"[.\s<>]+", text)
    words = [w for w in words if w and not w.startswith("$") and not w.startswith("!")]
    
    translated = []
    known = {}
    unknown = []
    
    for w in words:
        w_clean = w.strip("!?")
        if not w_clean:
            continue
        
        if w_clean == plant_word:
            translated.append(f"**{plant_name}**")
            known[w_clean] = plant_name
        elif w_clean in dictionary:
            meaning = dictionary[w_clean].get("meaning", "?")
            translated.append(f"[{meaning}]")
            known[w_clean] = meaning
        else:
            translated.append(f"{w_clean}")
            unknown.append(w_clean)
    
    return {
        "original_words": words,
        "translation": " ".join(translated),
        "known_words": known,
        "unknown_words": unknown,
        "coverage": len(known) / max(len(words), 1) * 100
    }


def analyze_patterns(all_contexts):
    """Analyze patterns across all plant contexts."""
    word_freq = Counter()
    unknown_freq = Counter()
    position_patterns = defaultdict(list)
    
    for ctx in all_contexts:
        line = ctx.get("full_line", "")
        words = re.split(r"[.\s<>]+", line)
        words = [w.strip("!?") for w in words if w and not w.startswith("$")]
        
        plant_word = ctx["voynich_word"]
        if plant_word in words:
            idx = words.index(plant_word)
            # Words before plant name
            if idx > 0:
                position_patterns["before_plant"].append(words[idx-1])
            if idx > 1:
                position_patterns["2_before_plant"].append(words[idx-2])
            # Words after plant name
            if idx < len(words) - 1:
                position_patterns["after_plant"].append(words[idx+1])
            if idx < len(words) - 2:
                position_patterns["2_after_plant"].append(words[idx+2])
        
        for w in words:
            word_freq[w] += 1
        
        for w in ctx.get("unknown_words", []):
            unknown_freq[w] += 1
    
    return {
        "word_frequency": dict(word_freq.most_common(30)),
        "unknown_frequency": dict(unknown_freq.most_common(20)),
        "position_patterns": {k: Counter(v).most_common(5) for k, v in position_patterns.items()}
    }


def propose_entries(pattern_analysis, dictionary, all_contexts):
    """Propose new dictionary entries based on patterns."""
    proposals = []
    
    # Words that appear frequently near plants
    before_counts = Counter(dict(pattern_analysis["position_patterns"].get("before_plant", [])))
    after_counts = Counter(dict(pattern_analysis["position_patterns"].get("after_plant", [])))
    
    # Common words appearing before plant names might be "take", "of", etc.
    for word, count in before_counts.items():
        if word not in dictionary and count >= 2:
            proposals.append({
                "word": word,
                "proposed_meaning": "preparation verb / preposition (appears before plant names)",
                "evidence": f"Appears {count}x directly before plant names",
                "confidence": "medium" if count >= 3 else "low"
            })
    
    # Common words appearing after plant names might be "for", "with", etc.
    for word, count in after_counts.items():
        if word not in dictionary and count >= 2:
            proposals.append({
                "word": word,
                "proposed_meaning": "purpose/use indicator (appears after plant names)",
                "evidence": f"Appears {count}x directly after plant names",
                "confidence": "medium" if count >= 3 else "low"
            })
    
    # Manual proposals based on context patterns observed
    manual_proposals = [
        # Words appearing immediately before plant names
        {
            "word": "chetaiin",
            "proposed_meaning": "ingredient marker / 'of (the plant)'",
            "evidence": "Appears before aconitum (shtshy) in f116r.13",
            "confidence": "medium",
            "context": "sar.aiin.tey.chetaiin.shtshy → barley.one.?.ingredient-marker.aconitum"
        },
        {
            "word": "saiin",
            "proposed_meaning": "seed / preparation (similar to 'semen')",
            "evidence": "Appears before ricinus (ychear) in f111v.22, similar to 'soiin' (seed)",
            "confidence": "medium",
            "context": "saiin.ychear → seed.ricinus (castor oil plant is famous for seeds)"
        },
        # Words appearing after plant names
        {
            "word": "opchedy",
            "proposed_meaning": "chest / pectoral (medical term)",
            "evidence": "Already in dict as 'chest', confirmed by appearing after ricinus",
            "confidence": "high",
            "context": "opchear.opchedy → ricinus.chest (ricinus used for chest ailments)"
        },
        # Words that seem to be recipe instruction markers
        {
            "word": "tshedar",
            "proposed_meaning": "pound/grind (preparation verb)",
            "evidence": "Appears at start of recipe line with papaver (opchar)",
            "confidence": "low",
            "context": "tshedar.chllo.rl.shed.kchedy.chokor.cheedy.opchar"
        },
        {
            "word": "tshedy",
            "proposed_meaning": "pound/grind (preparation verb)",
            "evidence": "Appears at start of recipe line with ricinus (opchear)",
            "confidence": "low",
            "context": "tshedy.qokaiin.shedar → prepare.priest.?"
        },
        # Quantity/measurement words
        {
            "word": "shal",
            "proposed_meaning": "part / portion (measurement)",
            "evidence": "Appears after scabiosa in recipe context",
            "confidence": "low",
            "context": "pair.ainckhe!dy.shal.kaiin → scabiosa.?.portion.priest"
        },
        # Anatomical/usage indicators
        {
            "word": "otal",
            "proposed_meaning": "whole / complete / all",
            "evidence": "Similar to Hebrew 'kol' (all), appears at end of recipe lines",
            "confidence": "medium",
            "context": "Appears in 'opchear.opchedy.lfchedy.otal'"
        },
        {
            "word": "okeedam",
            "proposed_meaning": "for remedy / medicinal use",
            "evidence": "Ends recipe line with aconitum",
            "confidence": "low",
            "context": "qoteedy.qokaiin.shety.okeedam → finger.priest.?.for-remedy"
        },
    ]
    
    # Add manual proposals that aren't in dictionary
    for p in manual_proposals:
        if p["word"] not in dictionary:
            proposals.append(p)
    
    return proposals


def main():
    print("=== Track 82: Deep Recipe Context Analysis ===\n")
    
    # Load data
    print("Loading EVA transcription...")
    folios = load_eva()
    print(f"  Loaded {len(folios)} folios")
    
    print("Loading dictionary...")
    dictionary = load_dict()
    print(f"  Loaded {len(dictionary)} entries")
    
    # Add mined plants to temp dictionary for translation
    for plant in HIGH_CONF_PLANTS:
        if plant["voynich"] not in dictionary:
            dictionary[plant["voynich"]] = {"meaning": plant["plant"], "source": "mined"}
    
    # Analyze each plant
    all_contexts = []
    
    print("\n=== Extracting Full Contexts ===\n")
    
    for plant in HIGH_CONF_PLANTS:
        print(f"\n--- {plant['voynich']} = {plant['plant']} ({plant['folio']}.{plant['line']}) ---")
        
        context = extract_context(folios, plant["folio"], plant["line"])
        if not context or not context["main_line"]:
            print(f"  WARNING: Could not find line {plant['line']} in {plant['folio']}")
            continue
        
        # Translate main line
        translation = translate_line(
            context["main_line"]["text"], 
            dictionary, 
            plant["voynich"], 
            plant["plant"]
        )
        
        print(f"\nFull line: {context['main_line']['text']}")
        print(f"Translation: {translation['translation']}")
        print(f"Coverage: {translation['coverage']:.1f}%")
        
        if context["context_before"]:
            print(f"\nContext before ({len(context['context_before'])} lines):")
            for ln in context["context_before"]:
                print(f"  [{ln['line']}] {ln['text']}")
        
        if context["context_after"]:
            print(f"\nContext after ({len(context['context_after'])} lines):")
            for ln in context["context_after"]:
                print(f"  [{ln['line']}] {ln['text']}")
        
        plant_context = {
            "plant": plant["plant"],
            "voynich_word": plant["voynich"],
            "folio": plant["folio"],
            "line_number": plant["line"],
            "full_line": context["main_line"]["text"],
            "context_before": [ln["text"] for ln in context["context_before"]],
            "context_after": [ln["text"] for ln in context["context_after"]],
            "translation": translation["translation"],
            "known_words": translation["known_words"],
            "unknown_words": translation["unknown_words"],
            "coverage": translation["coverage"]
        }
        all_contexts.append(plant_context)
    
    # Pattern analysis
    print("\n\n=== Pattern Analysis Across Plants ===\n")
    patterns = analyze_patterns(all_contexts)
    
    print("Top words appearing near plant names:")
    print(f"  Before plant: {patterns['position_patterns'].get('before_plant', [])}")
    print(f"  After plant: {patterns['position_patterns'].get('after_plant', [])}")
    
    print("\nMost frequent unknown words:")
    for w, c in list(patterns["unknown_frequency"].items())[:10]:
        print(f"  {w}: {c}x")
    
    # Propose new entries
    print("\n\n=== Proposed Dictionary Entries ===\n")
    proposals = propose_entries(patterns, dictionary, all_contexts)
    
    for p in proposals:
        print(f"  {p['word']}: {p['proposed_meaning']}")
        print(f"    Evidence: {p['evidence']}")
        print(f"    Confidence: {p['confidence']}\n")
    
    # Save results
    results = {
        "plants_analyzed": len(all_contexts),
        "full_contexts": all_contexts,
        "pattern_analysis": patterns,
        "proposed_entries": proposals,
        "avg_coverage": sum(c["coverage"] for c in all_contexts) / len(all_contexts) if all_contexts else 0
    }
    
    results_path = Path("results/recipe_context_analysis.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved analysis to {results_path}")
    
    # Generate report
    generate_report(all_contexts, patterns, proposals)
    
    return results


def generate_report(contexts, patterns, proposals):
    """Generate markdown report."""
    report = """# Recipe Context Analysis Report

## Summary

This analysis examines the 8 HIGH confidence plant names discovered in Track 79
and analyzes their contexts within recipe sections to build partial translations
and discover new vocabulary.

## Plants Analyzed

| Plant | Voynich Word | Recipe Folio | Coverage |
|-------|--------------|--------------|----------|
"""
    
    for ctx in contexts:
        report += f"| {ctx['plant']} | `{ctx['voynich_word']}` | {ctx['folio']}.{ctx['line_number']} | {ctx['coverage']:.1f}% |\n"
    
    report += "\n## Full Contexts & Translations\n\n"
    
    for ctx in contexts:
        report += f"### {ctx['plant'].title()} (`{ctx['voynich_word']}`)\n\n"
        report += f"**Folio**: {ctx['folio']}, Line {ctx['line_number']}\n\n"
        report += f"**Original**: `{ctx['full_line']}`\n\n"
        report += f"**Translation**: {ctx['translation']}\n\n"
        
        if ctx['known_words']:
            report += "**Known words**:\n"
            for w, m in list(ctx['known_words'].items())[:10]:
                report += f"- `{w}` → {m}\n"
        
        if ctx['unknown_words']:
            report += f"\n**Unknown**: {', '.join(ctx['unknown_words'][:10])}\n"
        
        report += "\n---\n\n"
    
    report += "## Pattern Analysis\n\n"
    report += "### Words Appearing Near Plant Names\n\n"
    
    for pos, items in patterns["position_patterns"].items():
        report += f"**{pos}**: {items}\n\n"
    
    report += "## Proposed New Dictionary Entries\n\n"
    report += "| Word | Proposed Meaning | Evidence | Confidence |\n"
    report += "|------|------------------|----------|------------|\n"
    
    for p in proposals:
        report += f"| `{p['word']}` | {p['proposed_meaning'][:40]} | {p['evidence']} | {p['confidence']} |\n"
    
    report += "\n## Key Findings\n\n"
    
    # Calculate avg coverage
    avg_cov = sum(c["coverage"] for c in contexts) / len(contexts) if contexts else 0
    report += f"1. **Average translation coverage**: {avg_cov:.1f}%\n"
    report += f"2. **Plants analyzed**: {len(contexts)}\n"
    report += f"3. **New vocabulary proposals**: {len(proposals)}\n"
    
    report_path = Path("results/recipe_context_report.md")
    with open(report_path, "w") as f:
        f.write(report)
    print(f"Saved report to {report_path}")


if __name__ == "__main__":
    main()
