"""
Track 31: Plant Label Key Derivation
Use visually-identified plants to derive/validate phonetic key through known plaintext analysis.
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher

from voynich_data import get_folio_text, convert_claston_to_eva

RESULTS_DIR = Path("results")

PLANT_IDS = [
    {"folio": "f17r", "visual_id": "Cornflower", "latin": "centaurea", "alt_latin": "cyanus", "confidence": 0.75, "label_claston": "f2o89"},
    {"folio": "f5r", "visual_id": "Hellebore", "latin": "helleborus", "alt_latin": None, "confidence": 0.60, "label_claston": "h2o89"},
    {"folio": "f2v", "visual_id": "Cyclamen", "latin": "cyclamen", "alt_latin": None, "confidence": 0.50, "label_claston": "hoom"},
    {"folio": "f4r", "visual_id": "Tamarisk", "latin": "tamarix", "alt_latin": None, "confidence": 0.50, "label_claston": "ho8ae19"},
    {"folio": "f6r", "visual_id": "Poppy", "latin": "papaver", "alt_latin": None, "confidence": 0.50, "label_claston": "foay"},
    {"folio": "f25v", "visual_id": "Castor Bean", "latin": "ricinus", "alt_latin": None, "confidence": 0.50, "label_claston": "goCam"},
    {"folio": "f3r", "visual_id": "Aloe", "latin": "aloe", "alt_latin": None, "confidence": 0.40, "label_claston": "k2cos"},
    {"folio": "f9r", "visual_id": "Oak", "latin": "quercus", "alt_latin": None, "confidence": 0.40, "label_claston": "k98eo"},
]

LATIN_DESCRIPTORS = [
    "flos", "folium", "radix", "herba", "cortex", "semen",
    "flores", "folia", "radices", "herbae", "cortices", "semina"
]

LATIN_USES = [
    "contra", "pro", "ad", "cum", "sine", "febrem", "dolorem", "tussis",
    "caput", "ventrem", "oculos", "vulnera"
]


def extract_first_words(folio, n=5):
    """Extract first n words from folio for label candidates."""
    text_data = get_folio_text(folio, system='EVA')
    if not text_data:
        return []
    
    words = []
    for loc in sorted(text_data.keys()):
        line = text_data[loc]
        line_clean = re.sub(r'[!?<>@$\[\]]', '', line)
        line_clean = re.sub(r'\{[^}]*\}', '', line_clean)
        for w in re.split(r'[.\-=,\s]+', line_clean):
            w = w.strip()
            if w and len(w) > 1 and not w.startswith('!'):
                words.append(w)
                if len(words) >= n:
                    return words
    return words


def derive_char_mapping(voynich, latin):
    """Attempt to derive character mapping from voynich label to latin name."""
    mappings = []
    v_lower = voynich.lower()
    l_lower = latin.lower()
    
    min_len = min(len(v_lower), len(l_lower))
    for i in range(min_len):
        mappings.append({
            "position": i + 1,
            "voynich_char": v_lower[i],
            "latin_char": l_lower[i]
        })
    
    return mappings


def check_mapping_consistency(all_mappings):
    """Check if derived mappings are consistent across plants."""
    char_map = defaultdict(list)
    for plant, mappings in all_mappings.items():
        for m in mappings:
            key = m["voynich_char"]
            char_map[key].append({
                "latin": m["latin_char"],
                "position": m["position"],
                "source": plant
            })
    
    consistent = []
    conflicts = []
    
    for v_char, derivations in char_map.items():
        latin_chars = set(d["latin"] for d in derivations)
        if len(latin_chars) == 1:
            consistent.append({
                "voynich": v_char,
                "latin": list(latin_chars)[0],
                "count": len(derivations),
                "sources": [d["source"] for d in derivations]
            })
        else:
            conflicts.append({
                "voynich": v_char,
                "derivations": derivations,
                "latin_options": list(latin_chars)
            })
    
    return consistent, conflicts


def similarity(a, b):
    """Calculate string similarity."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def test_descriptor_hypothesis(label_eva, descriptors):
    """Test if label might be a descriptor rather than plant name."""
    results = []
    for desc in descriptors:
        sim = similarity(label_eva, desc)
        if sim > 0.3:
            results.append({"descriptor": desc, "similarity": round(sim, 3)})
    return sorted(results, key=lambda x: -x["similarity"])[:3]


def analyze_label_patterns(plants):
    """Analyze patterns across all labels."""
    patterns = {
        "starting_chars": defaultdict(int),
        "ending_chars": defaultdict(int),
        "length_dist": defaultdict(int),
        "common_sequences": defaultdict(int)
    }
    
    for p in plants:
        label = p["label_claston"]
        if label:
            patterns["starting_chars"][label[0]] += 1
            patterns["ending_chars"][label[-1]] += 1
            patterns["length_dist"][len(label)] += 1
            for i in range(len(label) - 1):
                patterns["common_sequences"][label[i:i+2]] += 1
    
    return patterns


def run_derivation():
    """Main derivation analysis."""
    results = {
        "visual_ids_used": [],
        "derivation_attempts": [],
        "cross_check": {},
        "alternative_hypotheses": {},
        "patterns": {},
        "conclusion": ""
    }
    
    all_mappings = {}
    
    for plant in sorted(PLANT_IDS, key=lambda x: -x["confidence"]):
        label_claston = plant["label_claston"]
        label_eva = convert_claston_to_eva(label_claston)
        first_words = extract_first_words(plant["folio"])
        
        plant_entry = {
            "folio": plant["folio"],
            "visual_id": plant["visual_id"],
            "confidence": plant["confidence"],
            "label_claston": label_claston,
            "label_eva": label_eva,
            "first_words_eva": first_words[:3] if first_words else []
        }
        results["visual_ids_used"].append(plant_entry)
        
        for latin_name in [plant["latin"], plant["alt_latin"]]:
            if not latin_name:
                continue
            
            mappings = derive_char_mapping(label_eva, latin_name)
            direct_sim = similarity(label_eva, latin_name)
            
            attempt = {
                "folio": plant["folio"],
                "label_claston": label_claston,
                "label_eva": label_eva,
                "expected_latin": latin_name,
                "char_mappings": mappings,
                "length_match": len(label_eva) == len(latin_name),
                "length_diff": abs(len(label_eva) - len(latin_name)),
                "direct_similarity": round(direct_sim, 3),
                "plausibility": round(direct_sim * plant["confidence"], 3)
            }
            results["derivation_attempts"].append(attempt)
            
            if plant["confidence"] >= 0.5:
                all_mappings[f"{plant['folio']}_{latin_name}"] = mappings
    
    consistent, conflicts = check_mapping_consistency(all_mappings)
    results["cross_check"] = {
        "consistent_mappings": consistent,
        "conflicts": conflicts,
        "consistency_rate": len(consistent) / (len(consistent) + len(conflicts)) if (consistent or conflicts) else 0
    }
    
    descriptor_tests = {}
    for plant in PLANT_IDS:
        label_eva = convert_claston_to_eva(plant["label_claston"])
        desc_matches = test_descriptor_hypothesis(label_eva, LATIN_DESCRIPTORS)
        use_matches = test_descriptor_hypothesis(label_eva, LATIN_USES)
        if desc_matches or use_matches:
            descriptor_tests[plant["folio"]] = {
                "label": label_eva,
                "descriptor_matches": desc_matches,
                "use_matches": use_matches
            }
    
    results["alternative_hypotheses"] = {
        "labels_are_descriptions": descriptor_tests,
        "pattern_analysis": "See patterns section"
    }
    
    results["patterns"] = analyze_label_patterns(PLANT_IDS)
    results["patterns"] = {k: dict(v) for k, v in results["patterns"].items()}
    
    avg_similarity = sum(a["direct_similarity"] for a in results["derivation_attempts"]) / len(results["derivation_attempts"])
    conflict_rate = len(conflicts) / (len(consistent) + len(conflicts)) if (consistent or conflicts) else 1
    
    if avg_similarity < 0.3:
        conclusion = "NEGATIVE: Derived mappings show LOW similarity to expected Latin names"
        recommendation = "Labels are likely NOT direct plant names"
    elif conflict_rate > 0.5:
        conclusion = "INCONCLUSIVE: High conflict rate in character derivations"
        recommendation = "Labels may use inconsistent encoding or aren't plant names"
    else:
        conclusion = "PARTIAL: Some consistent mappings found"
        recommendation = "Further investigation needed with more samples"
    
    results["conclusion"] = conclusion
    results["recommendation"] = recommendation
    results["metrics"] = {
        "avg_similarity": round(avg_similarity, 3),
        "conflict_rate": round(conflict_rate, 3),
        "plants_analyzed": len(PLANT_IDS),
        "consistent_chars": len(consistent),
        "conflicting_chars": len(conflicts)
    }
    
    return results


def generate_report(results):
    """Generate markdown report."""
    lines = [
        "# Plant Label Key Derivation Report",
        "",
        "## Summary",
        f"- **Conclusion**: {results['conclusion']}",
        f"- **Recommendation**: {results['recommendation']}",
        "",
        "## Metrics",
        f"- Average direct similarity: {results['metrics']['avg_similarity']}",
        f"- Conflict rate: {results['metrics']['conflict_rate']}",
        f"- Plants analyzed: {results['metrics']['plants_analyzed']}",
        f"- Consistent character mappings: {results['metrics']['consistent_chars']}",
        f"- Conflicting character mappings: {results['metrics']['conflicting_chars']}",
        "",
        "## Visual Identifications Used",
        "",
        "| Folio | Plant | Confidence | Label (Claston) | Label (EVA) |",
        "|-------|-------|------------|-----------------|-------------|"
    ]
    
    for p in results["visual_ids_used"]:
        lines.append(f"| {p['folio']} | {p['visual_id']} | {p['confidence']} | {p['label_claston']} | {p['label_eva']} |")
    
    lines.extend([
        "",
        "## Derivation Attempts",
        ""
    ])
    
    for attempt in results["derivation_attempts"]:
        lines.extend([
            f"### {attempt['folio']} → {attempt['expected_latin']}",
            f"- Label (EVA): `{attempt['label_eva']}`",
            f"- Expected: `{attempt['expected_latin']}`",
            f"- Direct similarity: {attempt['direct_similarity']}",
            f"- Length match: {attempt['length_match']} (diff: {attempt['length_diff']})",
            f"- Plausibility score: {attempt['plausibility']}",
            "",
            "Character mappings:",
            "```"
        ])
        for m in attempt["char_mappings"][:8]:
            lines.append(f"  {m['position']}: {m['voynich_char']} → {m['latin_char']}")
        lines.append("```")
        lines.append("")
    
    lines.extend([
        "## Cross-Check Results",
        "",
        "### Consistent Mappings",
        ""
    ])
    
    if results["cross_check"]["consistent_mappings"]:
        for m in results["cross_check"]["consistent_mappings"]:
            lines.append(f"- `{m['voynich']}` → `{m['latin']}` (seen {m['count']} times)")
    else:
        lines.append("*No consistent mappings found*")
    
    lines.extend([
        "",
        "### Conflicts",
        ""
    ])
    
    if results["cross_check"]["conflicts"]:
        for c in results["cross_check"]["conflicts"][:10]:
            options = ", ".join(c["latin_options"])
            lines.append(f"- `{c['voynich']}` → [{options}]")
    else:
        lines.append("*No conflicts found*")
    
    lines.extend([
        "",
        "## Alternative Hypotheses",
        "",
        "### Labels as Descriptors",
        ""
    ])
    
    alt = results["alternative_hypotheses"]["labels_are_descriptions"]
    if alt:
        for folio, data in list(alt.items())[:5]:
            lines.append(f"**{folio}** ({data['label']})")
            if data["descriptor_matches"]:
                lines.append(f"  - Best descriptor match: {data['descriptor_matches'][0]}")
            if data["use_matches"]:
                lines.append(f"  - Best use match: {data['use_matches'][0]}")
            lines.append("")
    else:
        lines.append("*No significant descriptor matches found*")
    
    lines.extend([
        "",
        "## Label Patterns",
        ""
    ])
    
    patterns = results["patterns"]
    lines.append("Starting characters: " + str(dict(patterns["starting_chars"])))
    lines.append("")
    lines.append("Ending characters: " + str(dict(patterns["ending_chars"])))
    lines.append("")
    lines.append("Length distribution: " + str(dict(patterns["length_dist"])))
    
    lines.extend([
        "",
        "## Conclusion",
        "",
        results["conclusion"],
        "",
        "### Key Findings",
        ""
    ])
    
    if results["metrics"]["avg_similarity"] < 0.3:
        lines.append("1. **Low similarity**: Average similarity between labels and expected plant names is only "
                    f"{results['metrics']['avg_similarity']}, suggesting labels are NOT direct plant names.")
    
    if results["metrics"]["conflict_rate"] > 0.3:
        lines.append(f"2. **High conflict rate**: {results['metrics']['conflict_rate']*100:.0f}% of character derivations "
                    "conflict across plants, indicating no consistent cipher.")
    
    lines.extend([
        "",
        "### Implications",
        "",
        "The plant labels in the Voynich manuscript likely:",
        "- Are NOT direct Latin botanical names",
        "- May be abbreviated or coded descriptions",
        "- Could represent medicinal uses or locations",
        "- Might be in a non-Latin language entirely",
        "",
        "This negative result is valuable - it rules out simple substitution cipher for plant names."
    ])
    
    return "\n".join(lines)


def main():
    print("=" * 60)
    print("Track 31: Plant Label Key Derivation")
    print("=" * 60)
    
    results = run_derivation()
    
    json_path = RESULTS_DIR / "plant_key_derivation.json"
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {json_path}")
    
    report = generate_report(results)
    report_path = RESULTS_DIR / "plant_key_report.md"
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"Saved: {report_path}")
    
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"\nConclusion: {results['conclusion']}")
    print(f"Recommendation: {results['recommendation']}")
    print(f"\nMetrics:")
    for k, v in results["metrics"].items():
        print(f"  {k}: {v}")
    
    print("\n" + "-" * 60)
    print("Top Derivation Attempts:")
    for attempt in sorted(results["derivation_attempts"], key=lambda x: -x["plausibility"])[:3]:
        print(f"  {attempt['folio']}: {attempt['label_eva']} → {attempt['expected_latin']}")
        print(f"    Similarity: {attempt['direct_similarity']}, Plausibility: {attempt['plausibility']}")
    
    print("\n" + "-" * 60)
    print("Consistent Mappings Found:")
    for m in results["cross_check"]["consistent_mappings"][:5]:
        print(f"  {m['voynich']} → {m['latin']} (from {', '.join(m['sources'][:2])})")
    
    if results["cross_check"]["conflicts"]:
        print("\nConflicting Mappings:")
        for c in results["cross_check"]["conflicts"][:3]:
            print(f"  {c['voynich']} → {c['latin_options']}")
    
    return results


if __name__ == "__main__":
    main()
