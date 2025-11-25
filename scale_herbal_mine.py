"""
Track 80: Scale Unique Word Mining to ALL Herbal Pages

Methodology (proven in Track 79):
1. For each herbal folio
2. Find words RARE (<5 occurrences) on that page
3. Check if those rare words appear in recipe section (f103-f116)
4. If YES → candidate plant name
"""

import json
import re
from collections import defaultdict
from pathlib import Path

EVA_FILE = Path("data/eva_ivtff.txt")
RESULTS_DIR = Path("results")
TRACK79_FILE = RESULTS_DIR / "herbal_unique_words.json"
SCHOLARLY_FILE = RESULTS_DIR / "scholarly_master.json"

RECIPE_FOLIOS = [f"f{i}r" for i in range(103, 117)] + [f"f{i}v" for i in range(103, 117)]

ALL_HERBAL_PAGES = [
    "f1r", "f1v", "f2r", "f2v", "f3r", "f3v", "f4r", "f4v", "f5r", "f5v",
    "f6r", "f6v", "f7r", "f7v", "f8r", "f8v", "f9r", "f9v", "f10r", "f10v",
    "f11r", "f11v", "f13r", "f13v", "f14r", "f14v", "f15r", "f15v", "f16r", "f16v",
    "f17r", "f17v", "f18r", "f18v", "f19r", "f19v", "f20r", "f20v", "f21r", "f21v",
    "f22r", "f22v", "f23r", "f23v", "f24r", "f24v", "f25r", "f25v", "f26r", "f26v",
    "f27r", "f27v", "f28r", "f28v", "f29r", "f29v", "f30r", "f30v", "f31r", "f31v",
    "f32r", "f32v", "f33r", "f33v", "f34r", "f34v", "f35r", "f35v", "f36r", "f36v",
    "f37r", "f37v", "f38r", "f38v", "f39r", "f39v", "f40r", "f40v", "f41r", "f41v",
    "f42r", "f42v", "f43r", "f43v", "f44r", "f44v", "f45r", "f45v", "f46r", "f46v",
    "f47r", "f47v", "f48r", "f48v", "f49r", "f49v", "f50r", "f50v", "f51r", "f51v",
    "f52r", "f52v", "f53r", "f53v", "f54r", "f54v", "f55r", "f55v", "f56r", "f56v",
    "f57r", "f57v", "f65r", "f65v", "f66r", "f66v",
    "f87r", "f87v", "f89r1", "f89r2", "f89v1", "f89v2",
    "f90r1", "f90r2", "f90v1", "f90v2",
    "f93r", "f93v", "f94r", "f94v", "f95r1", "f95r2", "f95v1", "f95v2",
    "f96r", "f96v", "f99r", "f99v", "f100r", "f100v", "f101r", "f101v", "f102r1", "f102r2", "f102v1", "f102v2"
]

TRACK79_DONE = [
    "f3v", "f5v", "f6v", "f7r", "f8r", "f9v", "f10v", "f16r", "f17r", 
    "f24r", "f25r", "f33r", "f36v", "f48v", "f51r"
]


def load_eva_data():
    """Load and parse EVA transcription file."""
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
    """Build word rarity index across entire corpus."""
    word_stats = defaultdict(lambda: {"count": 0, "folios": set()})
    
    for folio, words in folio_words.items():
        for word in words:
            word_stats[word]["count"] += 1
            word_stats[word]["folios"].add(folio)
    
    for word in word_stats:
        word_stats[word]["folios"] = sorted(word_stats[word]["folios"])
    
    return dict(word_stats)


def load_expert_ids():
    """Load expert plant identifications from scholarly master."""
    expert_map = {}
    
    if SCHOLARLY_FILE.exists():
        with open(SCHOLARLY_FILE) as f:
            data = json.load(f)
        
        for item in data.get("new_vocabulary", []):
            plant_name = item.get("latin", "unknown")
            for folio in item.get("folios", []):
                if folio not in expert_map:
                    expert_map[folio] = []
                expert_map[folio].append(plant_name)
        
        for plant_name, info in data.get("top_plants", {}).items():
            for folio in info.get("folios", []):
                if folio not in expert_map:
                    expert_map[folio] = []
                if plant_name not in expert_map[folio]:
                    expert_map[folio].append(plant_name)
    
    return expert_map


def extract_rare_words(folio_words, rarity_index, target_folios, expert_map):
    """Extract rare words from each target herbal page."""
    results = {}
    
    for folio in target_folios:
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
        
        expert_ids = expert_map.get(folio, ["unknown"])
        
        results[folio] = {
            "folio": folio,
            "expert_id": expert_ids[0] if expert_ids else "unknown",
            "all_expert_ids": expert_ids,
            "total_words": len(folio_words[folio]),
            "unique_word_count": len(page_words),
            "unique_words": sorted(unique_words),
            "rare_words": sorted(rare_words, key=lambda x: x["total_occurrences"])
        }
    
    return results


def get_recipe_words(folio_lines):
    """Get all words from recipe section."""
    recipe_words = set()
    recipe_word_contexts = defaultdict(list)
    
    for folio in RECIPE_FOLIOS:
        if folio in folio_lines:
            for line_data in folio_lines[folio]:
                for word in line_data["words"]:
                    recipe_words.add(word)
                    recipe_word_contexts[word].append({
                        "folio": folio,
                        "loc": line_data["loc"],
                        "context": ".".join(line_data["words"][:10])
                    })
    
    return recipe_words, recipe_word_contexts


def crossref_with_recipes(herbal_data, recipe_words, recipe_contexts, rarity_index):
    """Cross-reference herbal rare words with recipe section."""
    crossref_results = []
    
    for folio, data in herbal_data.items():
        for rare in data["rare_words"]:
            word = rare["word"]
            
            recipe_folios = [f for f in rare["other_folios"] if f in RECIPE_FOLIOS]
            
            if recipe_folios or word in recipe_words:
                contexts = recipe_contexts.get(word, [])
                
                if rare["total_occurrences"] <= 2:
                    confidence = "HIGH"
                elif rare["total_occurrences"] <= 4:
                    confidence = "MEDIUM"
                else:
                    confidence = "LOW"
                
                if len(contexts) >= 3:
                    confidence = "HIGH"
                
                crossref_results.append({
                    "word": word,
                    "source_folio": folio,
                    "expert_plant": data["expert_id"],
                    "total_occurrences": rare["total_occurrences"],
                    "recipe_folios": list(set(c["folio"] for c in contexts)),
                    "recipe_occurrences": len(contexts),
                    "confidence": confidence
                })
    
    return sorted(crossref_results, key=lambda x: x["total_occurrences"])


def find_plant_pairs(herbal_data, rarity_index):
    """Find words shared between pages with same plant ID."""
    plant_folios = defaultdict(list)
    
    for folio, data in herbal_data.items():
        plant = data["expert_id"]
        if plant and plant != "unknown":
            plant_folios[plant].append(folio)
    
    pair_results = {}
    
    for plant, folios in plant_folios.items():
        if len(folios) < 2:
            continue
        
        word_sets = []
        for f in folios:
            if f in herbal_data:
                words = set(w["word"] for w in herbal_data[f]["rare_words"])
                word_sets.append(words)
        
        if len(word_sets) < 2:
            continue
        
        shared = word_sets[0]
        for ws in word_sets[1:]:
            shared = shared.intersection(ws)
        
        shared_exclusive = set()
        for word in shared:
            stats = rarity_index.get(word, {"folios": []})
            non_pair_folios = [f for f in stats["folios"] if f not in folios]
            
            if len(non_pair_folios) == 0:
                shared_exclusive.add(word)
            elif all(f.startswith(('f103', 'f104', 'f105', 'f106', 'f107', 'f108',
                                   'f109', 'f110', 'f111', 'f112', 'f113', 'f114',
                                   'f115', 'f116')) for f in non_pair_folios):
                shared_exclusive.add(word)
        
        if shared_exclusive:
            pair_results[plant] = {
                "plant": plant,
                "folios": folios,
                "shared_words": sorted(shared_exclusive),
                "count": len(shared_exclusive)
            }
    
    return pair_results


def build_dictionary_entries(crossref_results, pair_results):
    """Build dictionary entries from mining results."""
    entries = []
    seen_words = set()
    
    for result in crossref_results:
        word = result["word"]
        if word in seen_words:
            continue
        seen_words.add(word)
        
        entry = {
            "voynich": word,
            "meaning": result["expert_plant"],
            "confidence": result["confidence"].lower(),
            "evidence": {
                "source_folio": result["source_folio"],
                "recipe_folios": result["recipe_folios"],
                "total_occurrences": result["total_occurrences"]
            },
            "source": "herbal_mining_track80"
        }
        entries.append(entry)
    
    for plant, data in pair_results.items():
        for word in data["shared_words"]:
            if word in seen_words:
                continue
            seen_words.add(word)
            
            entry = {
                "voynich": word,
                "meaning": plant,
                "confidence": "high",
                "evidence": {
                    "shared_across_folios": data["folios"],
                    "plant_pair_validation": True
                },
                "source": "plant_pair_validation_track80"
            }
            entries.append(entry)
    
    return entries


def generate_report(stats, entries, crossref_results, pair_results, herbal_data):
    """Generate markdown report."""
    report = []
    report.append("# Track 80: Full-Scale Herbal Mining Results\n")
    report.append("## Methodology\n")
    report.append("Scale the unique word mining algorithm from Track 79 to ALL herbal pages.\n")
    report.append("Words **RARE** (<5 occurrences) on a plant page that **ALSO** appear in recipes")
    report.append("are likely **PLANT NAMES** used as ingredients.\n")
    
    report.append("## Summary Statistics\n")
    report.append("| Metric | Value |")
    report.append("|--------|-------|")
    report.append(f"| Total herbal pages analyzed | {stats['pages_analyzed']} |")
    report.append(f"| Pages with expert ID | {stats['pages_with_expert_id']} |")
    report.append(f"| Total unique words found | {stats['unique_words']} |")
    report.append(f"| Total rare words (<5 occ) | {stats['rare_words']} |")
    report.append(f"| **Rare words in recipes** | **{stats['rare_in_recipes']}** |")
    report.append(f"| Plant pairs found | {stats['plant_pairs']} |")
    report.append(f"| Pair-shared words | {stats['pair_shared_words']} |")
    report.append(f"| **New dictionary entries** | **{stats['new_entries']}** |")
    report.append(f"| HIGH confidence | {stats['high_conf']} |")
    report.append(f"| MEDIUM confidence | {stats['medium_conf']} |")
    report.append(f"| LOW confidence | {stats['low_conf']} |\n")
    
    report.append("## Key Findings\n")
    
    if crossref_results:
        report.append("### Top Plant-Recipe Crossreferences\n")
        report.append("| Word | Plant Page | Expert ID | Occurrences | Recipe Folios | Confidence |")
        report.append("|------|------------|-----------|-------------|---------------|------------|")
        for r in crossref_results[:30]:
            recipe_str = ", ".join(r["recipe_folios"][:3])
            if len(r["recipe_folios"]) > 3:
                recipe_str += "..."
            report.append(f"| `{r['word']}` | {r['source_folio']} | {r['expert_plant']} | {r['total_occurrences']} | {recipe_str} | {r['confidence']} |")
        report.append("")
    
    if pair_results:
        report.append("### Plant Pair Validations\n")
        report.append("Words appearing on MULTIPLE pages for the SAME plant:\n")
        for plant, data in pair_results.items():
            report.append(f"\n**{plant.upper()}** (folios: {', '.join(data['folios'][:5])})")
            report.append(f"- Shared exclusive words: {data['count']}")
            if data["shared_words"][:8]:
                report.append(f"- Examples: `{'`, `'.join(data['shared_words'][:8])}`")
        report.append("")
    
    report.append("### HIGH Confidence Entries\n")
    high_entries = [e for e in entries if e["confidence"] == "high"][:20]
    for e in high_entries:
        report.append(f"- `{e['voynich']}` = **{e['meaning']}**")
        if e.get("evidence", {}).get("recipe_folios"):
            report.append(f"  - Found in recipes: {', '.join(e['evidence']['recipe_folios'][:4])}")
    
    report.append("\n### MEDIUM Confidence Entries\n")
    med_entries = [e for e in entries if e["confidence"] == "medium"][:15]
    for e in med_entries:
        report.append(f"- `{e['voynich']}` = {e['meaning']}")
    
    report.append("\n## Coverage by Plant\n")
    plant_coverage = defaultdict(list)
    for e in entries:
        plant_coverage[e["meaning"]].append(e["voynich"])
    
    report.append("| Plant | Words Found |")
    report.append("|-------|-------------|")
    for plant, words in sorted(plant_coverage.items(), key=lambda x: -len(x[1]))[:20]:
        report.append(f"| {plant} | {len(words)} (`{'`, `'.join(words[:5])}`{'...' if len(words) > 5 else ''}) |")
    
    report.append("\n## Herbal Pages Summary\n")
    report.append("| Folio | Expert ID | Total Words | Unique | Rare | Rare in Recipes |")
    report.append("|-------|-----------|-------------|--------|------|-----------------|")
    for folio in sorted(herbal_data.keys()):
        data = herbal_data[folio]
        rare_in_recipe = sum(1 for r in crossref_results if r["source_folio"] == folio)
        report.append(f"| {folio} | {data['expert_id'][:20]} | {data['total_words']} | {data['unique_word_count']} | {len(data['rare_words'])} | {rare_in_recipe} |")
    
    report.append("\n---")
    report.append(f"\n*Track 80: Scaled from {len(TRACK79_DONE)} pages (Track 79) to {len(herbal_data)} pages*")
    
    return "\n".join(report)


def main():
    print("Track 80: Scale Unique Word Mining to ALL Herbal Pages")
    print("=" * 60)
    
    print("\n1. Loading EVA transcription data...")
    folio_words, folio_lines = load_eva_data()
    print(f"   Loaded {len(folio_words)} folios")
    
    print("\n2. Building rarity index...")
    rarity_index = build_rarity_index(folio_words)
    total_words = sum(stats["count"] for stats in rarity_index.values())
    rare_count = sum(1 for stats in rarity_index.values() if stats["count"] <= 5)
    print(f"   Total unique words: {len(rarity_index)}")
    print(f"   Total word tokens: {total_words}")
    print(f"   Rare words (<=5 occ): {rare_count}")
    
    print("\n3. Loading expert plant identifications...")
    expert_map = load_expert_ids()
    print(f"   Expert IDs for {len(expert_map)} folios")
    
    print("\n4. Extracting rare words from ALL herbal pages...")
    available_herbal = [f for f in ALL_HERBAL_PAGES if f in folio_words]
    herbal_data = extract_rare_words(folio_words, rarity_index, available_herbal, expert_map)
    print(f"   Analyzed {len(herbal_data)} herbal pages")
    
    print("\n5. Getting recipe section words...")
    recipe_words, recipe_contexts = get_recipe_words(folio_lines)
    print(f"   Recipe vocabulary: {len(recipe_words)} unique words")
    
    print("\n6. Cross-referencing with recipe section...")
    crossref_results = crossref_with_recipes(herbal_data, recipe_words, recipe_contexts, rarity_index)
    print(f"   Found {len(crossref_results)} rare words that appear in recipes")
    
    print("\n7. Finding plant pairs...")
    pair_results = find_plant_pairs(herbal_data, rarity_index)
    print(f"   Found {len(pair_results)} plant pairs with shared vocabulary")
    for plant, data in list(pair_results.items())[:5]:
        print(f"     - {plant}: {data['count']} shared words")
    
    print("\n8. Building dictionary entries...")
    entries = build_dictionary_entries(crossref_results, pair_results)
    print(f"   Generated {len(entries)} new dictionary entries")
    
    stats = {
        "pages_analyzed": len(herbal_data),
        "pages_with_expert_id": sum(1 for d in herbal_data.values() if d["expert_id"] != "unknown"),
        "unique_words": sum(len(d["unique_words"]) for d in herbal_data.values()),
        "rare_words": sum(len(d["rare_words"]) for d in herbal_data.values()),
        "rare_in_recipes": len(crossref_results),
        "plant_pairs": len(pair_results),
        "pair_shared_words": sum(d["count"] for d in pair_results.values()),
        "new_entries": len(entries),
        "high_conf": sum(1 for e in entries if e["confidence"] == "high"),
        "medium_conf": sum(1 for e in entries if e["confidence"] == "medium"),
        "low_conf": sum(1 for e in entries if e["confidence"] == "low")
    }
    
    print("\n9. Saving results...")
    RESULTS_DIR.mkdir(exist_ok=True)
    
    output = {
        "pages_analyzed": stats["pages_analyzed"],
        "combined_with_track79": True,
        "statistics": stats,
        "crossref_results": crossref_results,
        "plant_pairs": pair_results,
        "new_entries": entries,
        "high_confidence": stats["high_conf"],
        "medium_confidence": stats["medium_conf"],
        "herbal_page_data": herbal_data
    }
    
    with open(RESULTS_DIR / "full_herbal_mining.json", 'w') as f:
        json.dump(output, f, indent=2)
    
    report = generate_report(stats, entries, crossref_results, pair_results, herbal_data)
    with open(RESULTS_DIR / "full_herbal_mining_report.md", 'w') as f:
        f.write(report)
    
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total herbal pages analyzed: {stats['pages_analyzed']}")
    print(f"Pages with expert ID: {stats['pages_with_expert_id']}")
    print(f"Rare words in recipes: {stats['rare_in_recipes']}")
    print(f"Plant pairs found: {stats['plant_pairs']}")
    print(f"NEW DICTIONARY ENTRIES: {stats['new_entries']}")
    print(f"  - HIGH confidence: {stats['high_conf']}")
    print(f"  - MEDIUM confidence: {stats['medium_conf']}")
    print(f"  - LOW confidence: {stats['low_conf']}")
    
    if entries:
        print("\nTOP HIGH-CONFIDENCE ENTRIES:")
        for e in [e for e in entries if e["confidence"] == "high"][:15]:
            print(f"  {e['voynich']} = {e['meaning']}")
    
    print("\nOutput files:")
    print("  - results/full_herbal_mining.json")
    print("  - results/full_herbal_mining_report.md")


if __name__ == "__main__":
    main()
