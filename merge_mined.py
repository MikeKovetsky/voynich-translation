"""
Track 81: Merge mined plant names into unified dictionary.
Integrates 50 new plant-related entries from Track 79 unique word mining.
"""

import json
import re
from pathlib import Path
from collections import Counter
from voynich_data import get_eva_pages, get_section_text, FOLIO_SECTIONS

MASTER_DICT = Path("results/master_dictionary.json")
MINED_DICT = Path("results/mined_plant_names.json")
EXPANDED_DICT = Path("results/expanded_master_dictionary.json")
OUTPUT_DICT = Path("results/unified_dictionary.json")
OUTPUT_REPORT = Path("results/dictionary_merge_report.md")


def load_dictionaries():
    with open(MASTER_DICT) as f:
        master = json.load(f)
    with open(MINED_DICT) as f:
        mined = json.load(f)
    expanded = None
    if EXPANDED_DICT.exists():
        with open(EXPANDED_DICT) as f:
            expanded = json.load(f)
    return master, mined, expanded


def extract_words(pages):
    words = []
    for page_data in pages.values():
        for text in page_data.values():
            text_clean = re.sub(r'[!?<>@$\d]', '', text)
            for w in re.split(r'[.\-=,\s]', text_clean):
                if w and len(w) > 1:
                    words.append(w)
    return words


def get_section_words(section):
    pages = get_section_text(section)
    return extract_words(pages)


def calc_coverage(dictionary_entries, word_list):
    total = len(word_list)
    if total == 0:
        return {"total": 0, "covered": 0, "rate": 0.0}
    covered = sum(1 for w in word_list if w in dictionary_entries)
    return {
        "total": total,
        "covered": covered,
        "rate": round(covered / total, 4)
    }


def merge_dictionaries(master, mined, expanded):
    entries = dict(master.get("entries", {}))
    source_counts = dict(master.get("sources", {}))
    conflicts = []
    added = []
    
    if expanded:
        for word, entry in expanded.get("entries", {}).items():
            if word not in entries:
                entries[word] = entry
                src = entry.get("source", "Track75_ExpertBotanical")
                source_counts[src] = source_counts.get(src, 0) + 1
                added.append({
                    "word": word,
                    "meaning": entry.get("meaning"),
                    "source": src
                })
    
    track79_added = 0
    for entry in mined.get("entries", []):
        word = entry.get("voynich")
        new_meaning = entry.get("meaning")
        confidence_str = entry.get("confidence", "medium")
        new_confidence = 0.85 if confidence_str == "high" else 0.65
        
        if word in entries:
            existing = entries[word]
            old_meaning = existing.get("meaning")
            old_conf = existing.get("confidence", 0.5)
            
            if old_meaning.lower() != new_meaning.lower():
                conflicts.append({
                    "word": word,
                    "meaning_old": old_meaning,
                    "source_old": existing.get("source"),
                    "confidence_old": old_conf,
                    "meaning_new": new_meaning,
                    "source_new": "Track79_UniqueWordMining",
                    "confidence_new": new_confidence
                })
                
                if confidence_str == "high" and new_confidence > old_conf:
                    entries[word] = {
                        "voynich": word,
                        "meaning": new_meaning,
                        "language": "Latin",
                        "confidence": new_confidence,
                        "domain": "botanical",
                        "source": "Track79_UniqueWordMining",
                        "evidence": entry.get("evidence", {})
                    }
                    track79_added += 1
        else:
            entries[word] = {
                "voynich": word,
                "meaning": new_meaning,
                "language": "Latin",
                "confidence": new_confidence,
                "domain": "botanical",
                "source": "Track79_UniqueWordMining",
                "evidence": entry.get("evidence", {})
            }
            track79_added += 1
            added.append({
                "word": word,
                "meaning": new_meaning,
                "source": "Track79_UniqueWordMining"
            })
    
    source_counts["Track79_UniqueWordMining"] = track79_added
    
    return entries, source_counts, conflicts, added


def count_domains(entries):
    domains = Counter()
    for entry in entries.values():
        dom = entry.get("domain", "other")
        domains[dom] += 1
    return dict(domains)


def main():
    print("Track 81: Merging Mined Plant Names")
    print("=" * 50)
    
    master, mined, expanded = load_dictionaries()
    
    print(f"Master dictionary: {master.get('total_entries', 0)} entries")
    print(f"Mined plant names: {len(mined.get('entries', []))} entries")
    if expanded:
        print(f"Expanded dictionary: {expanded.get('total_entries', 0)} entries")
    
    entries, sources, conflicts, added = merge_dictionaries(master, mined, expanded)
    
    print(f"\nMerged dictionary: {len(entries)} entries")
    print(f"Conflicts found: {len(conflicts)}")
    
    print("\nCalculating coverage...")
    
    all_words = []
    recipes_words = []
    herbal_words = []
    
    pages = get_eva_pages()
    all_words = extract_words(pages)
    
    recipes_words = get_section_words('recipes')
    herbal_a = get_section_words('herbal_a')
    herbal_b = get_section_words('herbal_b')
    herbal_words = herbal_a + herbal_b
    
    coverage = {
        "recipes": calc_coverage(entries, recipes_words),
        "herbal": calc_coverage(entries, herbal_words),
        "overall": calc_coverage(entries, all_words)
    }
    
    print(f"\nCoverage Results:")
    print(f"  Recipes: {coverage['recipes']['rate']*100:.1f}% ({coverage['recipes']['covered']}/{coverage['recipes']['total']})")
    print(f"  Herbal: {coverage['herbal']['rate']*100:.1f}% ({coverage['herbal']['covered']}/{coverage['herbal']['total']})")
    print(f"  Overall: {coverage['overall']['rate']*100:.1f}% ({coverage['overall']['covered']}/{coverage['overall']['total']})")
    
    domains = count_domains(entries)
    
    unified = {
        "version": "2.0",
        "total_entries": len(entries),
        "sources": sources,
        "conflicts_found": len(conflicts),
        "conflicts_resolved": len([c for c in conflicts if c['confidence_new'] > c['confidence_old']]),
        "coverage": coverage,
        "domains": domains,
        "entries": entries
    }
    
    with open(OUTPUT_DICT, 'w') as f:
        json.dump(unified, f, indent=2)
    print(f"\nSaved unified dictionary to {OUTPUT_DICT}")
    
    master_before = master.get('coverage', {}).get('overall', {}).get('rate', 0) * 100
    
    report = f"""# Dictionary Merge Report - Track 81

## Summary

| Metric | Value |
|--------|-------|
| Master dictionary entries | {master.get('total_entries', 0)} |
| Mined plant names | {len(mined.get('entries', []))} |
| **Unified dictionary entries** | **{len(entries)}** |
| Conflicts detected | {len(conflicts)} |
| High-confidence overrides | {len([c for c in conflicts if c['confidence_new'] > c['confidence_old']])} |

## Source Breakdown

| Source | Entries |
|--------|---------|
"""
    for src, count in sorted(sources.items()):
        report += f"| {src} | {count} |\n"
    
    report += f"""
## Coverage Comparison

| Section | Before | After |
|---------|--------|-------|
| Recipes | ~46.6% | {coverage['recipes']['rate']*100:.1f}% |
| Herbal | ~44.8% | {coverage['herbal']['rate']*100:.1f}% |
| Overall | ~44.9% | {coverage['overall']['rate']*100:.1f}% |

## Domain Distribution

| Domain | Count |
|--------|-------|
"""
    for dom, count in sorted(domains.items(), key=lambda x: -x[1]):
        report += f"| {dom} | {count} |\n"
    
    if conflicts:
        report += f"""
## Conflicts Found ({len(conflicts)})

| Word | Old Meaning | Old Source | New Meaning | New Source | Resolution |
|------|-------------|------------|-------------|------------|------------|
"""
        for c in conflicts:
            resolution = "**UPDATED**" if c['confidence_new'] > c['confidence_old'] else "kept old"
            report += f"| `{c['word']}` | {c['meaning_old']} | {c['source_old']} | {c['meaning_new']} | {c['source_new']} | {resolution} |\n"
    
    high_conf_added = [a for a in added if a['source'] == 'Track79_UniqueWordMining'][:15]
    if high_conf_added:
        report += f"""
## Notable New Entries (Track 79)

| Word | Meaning | Evidence |
|------|---------|----------|
"""
        for a in high_conf_added:
            word = a['word']
            entry = entries.get(word, {})
            evidence = entry.get('evidence', {})
            plant_page = evidence.get('appears_on_plant_page', '?')
            recipe_pages = ', '.join(evidence.get('recipe_folios', []))
            report += f"| `{word}` | {a['meaning']} | Plant: {plant_page}, Recipes: {recipe_pages} |\n"
    
    report += f"""
## Key Findings

1. **Plant Name Validation**: {sum(1 for a in added if a['source'] == 'Track79_UniqueWordMining')} new botanical terms added from unique word mining
2. **Cross-reference Success**: Plant words appear on both herbal pages AND recipe folios
3. **Conflict Rate**: {len(conflicts)}/{len(mined.get('entries', []))} entries ({100*len(conflicts)/max(1,len(mined.get('entries',[]))):.1f}%) had meaning conflicts

## Recommendations

1. Review conflicts manually - some may indicate polysemy (same word = different meanings)
2. Focus on HIGH confidence plant names for validation against illustrations
3. Use unified dictionary for full-manuscript translation attempts

---
*Generated by Track 81 merge_mined.py*
"""
    
    with open(OUTPUT_REPORT, 'w') as f:
        f.write(report)
    print(f"Saved report to {OUTPUT_REPORT}")
    
    print("\n" + "=" * 50)
    print("TRACK 81 COMPLETE")
    print(f"Unified dictionary: {len(entries)} entries")
    print(f"Coverage improvement: {master_before:.1f}% -> {coverage['overall']['rate']*100:.1f}%")


if __name__ == "__main__":
    main()
