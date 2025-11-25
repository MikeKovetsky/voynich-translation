"""
Track 79: Unique Word Mining Algorithm

Methodology: Words UNIQUE to a plant page that ALSO appear in recipes 
are likely the PLANT NAME used as ingredient.
"""

import json
import re
from collections import defaultdict
from pathlib import Path

EVA_FILE = Path("data/eva_ivtff.txt")
RESULTS_DIR = Path("results")

HERBAL_TARGETS = {
    "f16r": {"expert_id": "aconitum", "alt_id": "cannabis?", "priority": "HIGH"},
    "f9v": {"expert_id": "viola", "priority": "HIGH"},
    "f6v": {"expert_id": "ricinus", "priority": "HIGH"},
    "f51r": {"expert_id": "ricinus", "priority": "HIGH"},
    "f36v": {"expert_id": "cannabis", "priority": "MEDIUM"},
    "f7r": {"expert_id": "paeonia", "priority": "MEDIUM"},
    "f17r": {"expert_id": "smilax", "priority": "MEDIUM"},
    "f25r": {"expert_id": "mentastrum", "priority": "MEDIUM"},
    "f33r": {"expert_id": "scabiosa", "priority": "MEDIUM"},
    "f48v": {"expert_id": "papaver", "priority": "HIGH"},
    "f3v": {"expert_id": "hypericum", "priority": "MEDIUM"},
    "f5v": {"expert_id": "geranium", "priority": "MEDIUM"},
    "f8r": {"expert_id": "atriplex", "priority": "MEDIUM"},
    "f10v": {"expert_id": "papaver", "priority": "HIGH"},
    "f24r": {"expert_id": "papaver", "priority": "HIGH"},
}

PLANT_PAIRS = {
    "ricinus": ["f6v", "f51r"],
    "papaver": ["f10v", "f48v", "f24r"],
}

RECIPE_FOLIOS = [f"f{i}r" for i in range(103, 117)] + [f"f{i}v" for i in range(103, 117)]

PLANT_SKELETONS = {
    "viola": ["vl", "sgl", "viol"],
    "ricinus": ["rcn", "qqn", "rcns", "kqyn"],
    "paeonia": ["pn", "paon", "peon"],
    "cannabis": ["cnbs", "qnbs", "cnp", "knbs", "hashish"],
    "papaver": ["ppvr", "ppv", "afyon"],
    "hypericum": ["hprcm", "prprn", "ipric"],
    "geranium": ["grnm", "grn"],
    "atriplex": ["trplx", "atrplx"],
    "smilax": ["smlx", "smlk"],
    "mentastrum": ["mntstrm", "mnt"],
    "scabiosa": ["scbs", "skbs"],
    "aconitum": ["cntm", "acnt"],
}


def load_eva_data():
    """Load and parse EVA transcription file."""
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


def build_rarity_index(folio_words):
    """Build word rarity index: count occurrences and list folios."""
    word_stats = defaultdict(lambda: {"count": 0, "folios": set()})
    
    for folio, words in folio_words.items():
        for word in words:
            word_stats[word]["count"] += 1
            word_stats[word]["folios"].add(folio)
    
    for word in word_stats:
        word_stats[word]["folios"] = sorted(word_stats[word]["folios"])
    
    return dict(word_stats)


def extract_unique_words_per_herbal(folio_words, rarity_index):
    """Extract unique/rare words from each herbal target page."""
    results = {}
    
    for folio, info in HERBAL_TARGETS.items():
        if folio not in folio_words:
            continue
        
        page_words = set(folio_words[folio])
        unique_words = []
        rare_words = []
        
        for word in page_words:
            stats = rarity_index.get(word, {"count": 0, "folios": []})
            
            if stats["count"] == 1:
                unique_words.append(word)
            
            if stats["count"] <= 5:
                other_folios = [f for f in stats["folios"] if f != folio]
                rare_words.append({
                    "word": word,
                    "total_occurrences": stats["count"],
                    "other_folios": other_folios
                })
        
        results[folio] = {
            "folio": folio,
            "expert_id": info["expert_id"],
            "priority": info["priority"],
            "total_words": len(folio_words[folio]),
            "unique_word_count": len(page_words),
            "unique_words": sorted(unique_words),
            "rare_words": sorted(rare_words, key=lambda x: x["total_occurrences"])
        }
    
    return results


def crossref_with_recipes(herbal_unique, rarity_index, folio_lines):
    """Cross-reference rare herbal words with recipe section."""
    recipe_words = set()
    for folio in RECIPE_FOLIOS:
        if folio in folio_lines:
            for line_data in folio_lines[folio]:
                recipe_words.update(line_data["words"])
    
    crossref_results = []
    
    for folio, data in herbal_unique.items():
        for rare in data["rare_words"]:
            word = rare["word"]
            
            recipe_folios = [f for f in rare["other_folios"] if f in RECIPE_FOLIOS]
            
            if recipe_folios or word in recipe_words:
                recipe_contexts = []
                for rf in RECIPE_FOLIOS:
                    if rf in folio_lines:
                        for line_data in folio_lines[rf]:
                            if word in line_data["words"]:
                                context_words = line_data["words"]
                                idx = context_words.index(word)
                                start = max(0, idx - 2)
                                end = min(len(context_words), idx + 3)
                                context = ".".join(context_words[start:end])
                                recipe_contexts.append({
                                    "folio": rf,
                                    "loc": line_data["loc"],
                                    "context": context
                                })
                
                confidence = "HIGH" if rare["total_occurrences"] <= 2 else "MEDIUM"
                if len(recipe_contexts) > 2:
                    confidence = "HIGH"
                
                crossref_results.append({
                    "word": word,
                    "source_folio": folio,
                    "expert_plant": data["expert_id"],
                    "total_occurrences": rare["total_occurrences"],
                    "recipe_occurrences": recipe_contexts,
                    "confidence": confidence
                })
    
    return sorted(crossref_results, key=lambda x: x["total_occurrences"])


def validate_plant_pairs(folio_words, rarity_index):
    """Find words appearing on BOTH pages of a plant pair but nowhere else."""
    pair_vocabulary = {}
    
    for plant, folios in PLANT_PAIRS.items():
        shared_unique = set()
        
        available_folios = [f for f in folios if f in folio_words]
        if len(available_folios) < 2:
            continue
        
        words_per_folio = [set(folio_words[f]) for f in available_folios]
        shared = words_per_folio[0].intersection(*words_per_folio[1:])
        
        for word in shared:
            stats = rarity_index.get(word, {"count": 0, "folios": []})
            non_pair_folios = [f for f in stats["folios"] if f not in folios]
            
            if len(non_pair_folios) == 0:
                shared_unique.add(word)
            elif len(non_pair_folios) <= 2:
                if all(f.startswith(('f103', 'f104', 'f105', 'f106', 'f107', 'f108', 
                                      'f109', 'f110', 'f111', 'f112', 'f113', 'f114', 
                                      'f115', 'f116')) for f in non_pair_folios):
                    shared_unique.add(word)
        
        pair_vocabulary[plant] = {
            "plant": plant,
            "folios": available_folios,
            "shared_unique_words": sorted(shared_unique),
            "total_shared": len(shared),
            "unique_count": len(shared_unique)
        }
    
    return pair_vocabulary


def compute_skeleton(word):
    """Compute consonant skeleton of a word."""
    vowels = set('aeiou')
    return ''.join(c for c in word.lower() if c not in vowels)


def match_skeleton(word, plant_name):
    """Check if word skeleton matches any plant name pattern."""
    word_skeleton = compute_skeleton(word)
    patterns = PLANT_SKELETONS.get(plant_name, [])
    
    for pattern in patterns:
        if pattern in word_skeleton or word_skeleton in pattern:
            return True, pattern
        if len(word_skeleton) >= 3 and len(pattern) >= 3:
            if word_skeleton[:3] == pattern[:3]:
                return True, pattern
    
    return False, None


def build_dictionary_entries(crossref_results, pair_vocabulary):
    """Build new dictionary entries from validated plant words."""
    entries = []
    
    for result in crossref_results:
        word = result["word"]
        plant = result["expert_plant"]
        
        skeleton_match, matched_pattern = match_skeleton(word, plant)
        
        evidence = {
            "appears_on_plant_page": result["source_folio"],
            "expert_id": plant,
            "appears_in_recipes": len(result["recipe_occurrences"]) > 0,
            "recipe_folios": list(set(r["folio"] for r in result["recipe_occurrences"])),
            "total_manuscript_occurrences": result["total_occurrences"]
        }
        
        confidence = result["confidence"].lower()
        if skeleton_match:
            confidence = "high"
            evidence["skeleton_match"] = matched_pattern
        
        entry = {
            "voynich": word,
            "meaning": plant,
            "confidence": confidence,
            "evidence": evidence,
            "source": "unique_word_mining"
        }
        entries.append(entry)
    
    for plant, data in pair_vocabulary.items():
        for word in data["shared_unique_words"]:
            if any(e["voynich"] == word for e in entries):
                continue
            
            skeleton_match, matched_pattern = match_skeleton(word, plant)
            
            entry = {
                "voynich": word,
                "meaning": plant,
                "confidence": "high" if skeleton_match else "medium",
                "evidence": {
                    "appears_on_plant_pages": data["folios"],
                    "expert_id": plant,
                    "shared_across_pair": True,
                    "appears_nowhere_else": True
                },
                "source": "plant_pair_validation"
            }
            if skeleton_match:
                entry["evidence"]["skeleton_match"] = matched_pattern
            entries.append(entry)
    
    return entries


def generate_statistics(herbal_unique, crossref_results, pair_vocabulary, entries, rarity_index):
    """Generate summary statistics."""
    total_rare_words = sum(len(data["rare_words"]) for data in herbal_unique.values())
    rare_in_recipes = len(crossref_results)
    
    high_conf = sum(1 for e in entries if e["confidence"] == "high")
    medium_conf = sum(1 for e in entries if e["confidence"] == "medium")
    
    return {
        "herbal_pages_analyzed": len(herbal_unique),
        "total_unique_words_found": sum(len(data["unique_words"]) for data in herbal_unique.values()),
        "total_rare_words_found": total_rare_words,
        "rare_words_in_recipes": rare_in_recipes,
        "plant_pairs_analyzed": len(pair_vocabulary),
        "pair_shared_unique_words": sum(data["unique_count"] for data in pair_vocabulary.values()),
        "new_dictionary_entries": len(entries),
        "high_confidence_entries": high_conf,
        "medium_confidence_entries": medium_conf,
        "coverage_before": 0,
        "estimated_coverage_gain": f"+{len(entries)} entries"
    }


def generate_report(stats, entries, crossref_results, pair_vocabulary, herbal_unique):
    """Generate markdown report."""
    report = []
    report.append("# Track 79: Unique Word Mining Results\n")
    report.append("## Methodology\n")
    report.append("Words **UNIQUE** to a plant page that **ALSO** appear in recipes")
    report.append("are likely the **PLANT NAME** used as ingredient.\n")
    
    report.append("## Summary Statistics\n")
    report.append("| Metric | Value |")
    report.append("|--------|-------|")
    report.append(f"| Herbal pages analyzed | {stats['herbal_pages_analyzed']} |")
    report.append(f"| Unique words found | {stats['total_unique_words_found']} |")
    report.append(f"| Rare words found (<5 occurrences) | {stats['total_rare_words_found']} |")
    report.append(f"| Rare words also in recipes | {stats['rare_words_in_recipes']} |")
    report.append(f"| Plant pairs analyzed | {stats['plant_pairs_analyzed']} |")
    report.append(f"| Pair-shared unique words | {stats['pair_shared_unique_words']} |")
    report.append(f"| **New dictionary entries** | **{stats['new_dictionary_entries']}** |")
    report.append(f"| High confidence | {stats['high_confidence_entries']} |")
    report.append(f"| Medium confidence | {stats['medium_confidence_entries']} |\n")
    
    report.append("## Key Findings\n")
    
    if crossref_results:
        report.append("### Top Plant-Recipe Crossreferences\n")
        report.append("| Word | Source Page | Plant | Occurrences | Recipe Folios | Confidence |")
        report.append("|------|-------------|-------|-------------|---------------|------------|")
        for r in crossref_results[:20]:
            recipe_folios = ", ".join(set(o["folio"] for o in r["recipe_occurrences"]))[:30]
            report.append(f"| `{r['word']}` | {r['source_folio']} | {r['expert_plant']} | {r['total_occurrences']} | {recipe_folios} | {r['confidence']} |")
        report.append("")
    
    if pair_vocabulary:
        report.append("### Plant Pair Validation\n")
        report.append("Words appearing on MULTIPLE pages for SAME plant:\n")
        for plant, data in pair_vocabulary.items():
            if data["unique_count"] > 0:
                report.append(f"\n**{plant.upper()}** (folios: {', '.join(data['folios'])})")
                report.append(f"- Shared unique words: {data['unique_count']}")
                if data["shared_unique_words"][:10]:
                    report.append(f"- Examples: `{'`, `'.join(data['shared_unique_words'][:10])}`")
        report.append("")
    
    if entries:
        report.append("## New Dictionary Entries\n")
        report.append("### High Confidence\n")
        high_entries = [e for e in entries if e["confidence"] == "high"]
        for e in high_entries[:15]:
            evidence = e.get("evidence", {})
            report.append(f"- `{e['voynich']}` = **{e['meaning']}**")
            if "skeleton_match" in evidence:
                report.append(f"  - Skeleton match: {evidence['skeleton_match']}")
            if evidence.get("recipe_folios"):
                report.append(f"  - Found in recipes: {', '.join(evidence['recipe_folios'][:5])}")
        
        report.append("\n### Medium Confidence\n")
        med_entries = [e for e in entries if e["confidence"] == "medium"]
        for e in med_entries[:10]:
            report.append(f"- `{e['voynich']}` = {e['meaning']}")
    
    report.append("\n## Herbal Page Details\n")
    for folio, data in sorted(herbal_unique.items()):
        report.append(f"\n### {folio} ({data['expert_id']})")
        report.append(f"- Total words: {data['total_words']}")
        report.append(f"- Unique words: {len(data['unique_words'])}")
        report.append(f"- Rare words: {len(data['rare_words'])}")
        if data["unique_words"][:5]:
            report.append(f"- Examples: `{'`, `'.join(data['unique_words'][:5])}`")
    
    report.append("\n---")
    report.append(f"\n*Generated by Track 79: Unique Word Mining Algorithm*")
    
    return "\n".join(report)


def main():
    print("Track 79: Unique Word Mining Algorithm")
    print("=" * 50)
    
    print("\n1. Loading EVA transcription data...")
    folio_words, folio_lines = load_eva_data()
    print(f"   Loaded {len(folio_words)} folios")
    
    print("\n2. Building rarity index...")
    rarity_index = build_rarity_index(folio_words)
    total_words = sum(stats["count"] for stats in rarity_index.values())
    rare_count = sum(1 for stats in rarity_index.values() if stats["count"] <= 5)
    print(f"   Total unique words: {len(rarity_index)}")
    print(f"   Total word tokens: {total_words}")
    print(f"   Rare words (<=5 occurrences): {rare_count}")
    
    print("\n3. Extracting unique words per herbal page...")
    herbal_unique = extract_unique_words_per_herbal(folio_words, rarity_index)
    print(f"   Analyzed {len(herbal_unique)} herbal pages")
    
    print("\n4. Cross-referencing with recipe section...")
    crossref_results = crossref_with_recipes(herbal_unique, rarity_index, folio_lines)
    print(f"   Found {len(crossref_results)} rare words that appear in recipes")
    
    print("\n5. Validating plant pairs...")
    pair_vocabulary = validate_plant_pairs(folio_words, rarity_index)
    for plant, data in pair_vocabulary.items():
        print(f"   {plant}: {data['unique_count']} shared unique words")
    
    print("\n6. Building dictionary entries...")
    entries = build_dictionary_entries(crossref_results, pair_vocabulary)
    print(f"   Generated {len(entries)} new dictionary entries")
    
    print("\n7. Generating statistics...")
    stats = generate_statistics(herbal_unique, crossref_results, pair_vocabulary, entries, rarity_index)
    
    print("\n8. Saving results...")
    RESULTS_DIR.mkdir(exist_ok=True)
    
    rarity_output = {
        "total_unique_words": len(rarity_index),
        "rare_word_count": rare_count,
        "sample_rare": {k: v for k, v in list(rarity_index.items())[:100] if v["count"] <= 5}
    }
    with open(RESULTS_DIR / "word_rarity_index.json", 'w') as f:
        json.dump(rarity_output, f, indent=2)
    
    with open(RESULTS_DIR / "herbal_unique_words.json", 'w') as f:
        json.dump(herbal_unique, f, indent=2)
    
    with open(RESULTS_DIR / "plant_recipe_crossref.json", 'w') as f:
        json.dump(crossref_results, f, indent=2)
    
    with open(RESULTS_DIR / "plant_pair_vocabulary.json", 'w') as f:
        json.dump(pair_vocabulary, f, indent=2)
    
    with open(RESULTS_DIR / "mined_plant_names.json", 'w') as f:
        json.dump({"statistics": stats, "entries": entries}, f, indent=2)
    
    report = generate_report(stats, entries, crossref_results, pair_vocabulary, herbal_unique)
    with open(RESULTS_DIR / "unique_word_mining_report.md", 'w') as f:
        f.write(report)
    
    print("\n" + "=" * 50)
    print("RESULTS SUMMARY")
    print("=" * 50)
    print(f"Herbal pages analyzed: {stats['herbal_pages_analyzed']}")
    print(f"Rare words in recipes: {stats['rare_words_in_recipes']}")
    print(f"NEW DICTIONARY ENTRIES: {stats['new_dictionary_entries']}")
    print(f"  - High confidence: {stats['high_confidence_entries']}")
    print(f"  - Medium confidence: {stats['medium_confidence_entries']}")
    
    if entries:
        print("\nTOP NEW ENTRIES:")
        for e in entries[:10]:
            print(f"  {e['voynich']} = {e['meaning']} ({e['confidence']})")
    
    print("\nOutput files:")
    print("  - results/word_rarity_index.json")
    print("  - results/herbal_unique_words.json")
    print("  - results/plant_recipe_crossref.json")
    print("  - results/plant_pair_vocabulary.json")
    print("  - results/mined_plant_names.json")
    print("  - results/unique_word_mining_report.md")


if __name__ == "__main__":
    main()
