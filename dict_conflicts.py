import json
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path("results")

SEMANTIC_DOMAINS = {
    "botanical": ["plant", "herb", "tree", "seed", "flower", "root", "leaf", "wheat", "barley", "fig", "garlic", "aloe", "lily", "branch"],
    "medical": ["blood", "sick", "finger", "eye", "ear", "milk", "chest", "kidney", "cure", "fever", "heart"],
    "astronomical": ["taurus", "capricorn", "aries", "sky", "year", "sun", "moon", "star"],
    "pharmaceutical": ["give", "vinegar", "oil", "eat", "salt", "medicine", "drug"],
    "number": ["one", "two", "three", "all"],
    "grammar": ["the", "of", "from", "to", "and", "is", "for", "with", "verb", "noun"],
}

def get_domain(meaning):
    m = meaning.lower()
    for domain, keywords in SEMANTIC_DOMAINS.items():
        for kw in keywords:
            if kw in m:
                return domain
    return "other"

def load_dicts():
    dicts = {}
    
    files = [
        ("hybrid", "hybrid_dictionary.json"),
        ("semantic", "dictionary_expansion_semantic.json"),
        ("freq", "dictionary_expansion_freq.json"),
        ("context", "dictionary_expansion_context.json"),
    ]
    
    for name, fname in files:
        path = DATA_DIR / fname
        if path.exists():
            with open(path) as f:
                dicts[name] = json.load(f)
    return dicts

def extract_all_meanings(dicts):
    word_meanings = defaultdict(list)
    
    if "hybrid" in dicts:
        entries = dicts["hybrid"].get("entries", {})
        for word, data in entries.items():
            meanings = data.get("meanings", [])
            for m in meanings:
                meaning = m.get("translation", "")
                word_meanings[word].append({
                    "meaning": meaning,
                    "source": "hybrid",
                    "language": m.get("language", "unknown"),
                    "confidence": m.get("confidence", 0),
                    "domain": get_domain(meaning),
                })
    
    if "semantic" in dicts:
        for domain, domain_data in dicts["semantic"].get("domains", {}).items():
            for entry in domain_data.get("entries", []):
                word = entry.get("voynich", "")
                meaning = entry.get("meaning", "")
                word_meanings[word].append({
                    "meaning": meaning,
                    "source": f"semantic_{domain}",
                    "language": entry.get("language", "unknown"),
                    "confidence": 0.6,
                    "domain": domain,
                })
    
    if "freq" in dicts:
        entries = dicts["freq"].get("entries", {})
        for word, data in entries.items():
            meaning = data.get("meaning", "")
            if meaning:
                word_meanings[word].append({
                    "meaning": meaning,
                    "source": "freq",
                    "language": data.get("language", "unknown"),
                    "confidence": data.get("confidence", 0.5),
                    "domain": get_domain(meaning),
                })
    
    if "context" in dicts:
        entries = dicts["context"].get("entries", {})
        for word, data in entries.items():
            meaning = data.get("meaning", "")
            if meaning:
                word_meanings[word].append({
                    "meaning": meaning,
                    "source": "context",
                    "language": "inferred",
                    "confidence": data.get("confidence", 0.5),
                    "domain": get_domain(meaning),
                })
    
    return word_meanings

def categorize_conflict(meanings):
    unique_meanings = set()
    unique_domains = set()
    
    for m in meanings:
        meaning = m["meaning"].lower().strip()
        if meaning and meaning not in ["unknown", "verb form", "the (+ noun)", "verbal/adjectival"]:
            unique_meanings.add(meaning)
            unique_domains.add(m["domain"])
    
    if len(unique_meanings) <= 1:
        return "no_conflict", unique_meanings
    
    if len(unique_domains) == 1:
        return "same_domain", unique_meanings
    
    grammar_words = {"the", "of", "from", "to", "is", "and", "for", "with", "one", "all"}
    content_meanings = [m for m in unique_meanings if m not in grammar_words and "verb" not in m]
    grammar_meanings = unique_meanings - set(content_meanings)
    
    if content_meanings and grammar_meanings:
        return "grammar_vs_content", unique_meanings
    
    return "cross_domain", unique_meanings

def find_conflicts(word_meanings):
    conflicts = []
    clean = []
    
    for word, meanings in word_meanings.items():
        conflict_type, unique = categorize_conflict(meanings)
        
        if conflict_type == "no_conflict":
            best = max(meanings, key=lambda x: x.get("confidence", 0))
            clean.append({
                "voynich": word,
                "meaning": best["meaning"],
                "language": best["language"],
                "confidence": best["confidence"],
                "domain": best["domain"],
            })
        else:
            conflicts.append({
                "voynich": word,
                "conflict_type": conflict_type,
                "meanings": list(unique),
                "sources": list(set(m["source"] for m in meanings)),
                "domains": list(set(m["domain"] for m in meanings)),
                "all_entries": meanings,
            })
    
    return conflicts, clean

def calculate_coverage(clean_dict):
    from collections import Counter
    
    try:
        with open("data/eva_ivtff.txt") as f:
            text = f.read()
        
        words = []
        for line in text.split("\n"):
            if line.startswith("#") or not line.strip():
                continue
            if "<" in line and ">" in line:
                parts = line.split(">")
                if len(parts) > 1:
                    content = parts[-1]
                    for w in content.replace(".", " ").replace(",", " ").replace("-", " ").split():
                        if w and w.isalpha():
                            words.append(w)
        
        freq = Counter(words)
        total = len(words)
        
        clean_words = {e["voynich"] for e in clean_dict}
        matched = sum(freq[w] for w in clean_words if w in freq)
        
        top_100 = freq.most_common(100)
        top_100_in_clean = sum(1 for w, c in top_100 if w in clean_words)
        top_100_coverage = sum(c for w, c in top_100 if w in clean_words) / sum(c for w, c in top_100) * 100
        
        return {
            "total_words": total,
            "unique_words": len(freq),
            "matched_words": matched,
            "coverage": round(matched / total * 100, 2) if total > 0 else 0,
            "top_100_words_matched": f"{top_100_in_clean}/100",
            "top_100_coverage": round(top_100_coverage, 2),
        }
    except Exception as e:
        return {"error": str(e), "coverage": 0}

def analyze_worst_offenders(conflicts):
    sorted_conflicts = sorted(conflicts, key=lambda x: len(x["meanings"]), reverse=True)
    
    worst = []
    for c in sorted_conflicts[:20]:
        worst.append({
            "word": c["voynich"],
            "num_meanings": len(c["meanings"]),
            "meanings": c["meanings"][:5],
            "conflict_type": c["conflict_type"],
            "domains": c["domains"],
        })
    return worst

def main():
    print("Loading dictionaries...")
    dicts = load_dicts()
    
    print(f"Loaded: {list(dicts.keys())}")
    
    print("\nExtracting all meanings...")
    word_meanings = extract_all_meanings(dicts)
    print(f"Total unique words: {len(word_meanings)}")
    
    print("\nFinding conflicts...")
    conflicts, clean = find_conflicts(word_meanings)
    
    by_type = defaultdict(list)
    for c in conflicts:
        by_type[c["conflict_type"]].append(c)
    
    print(f"\nConflict summary:")
    print(f"  Total entries analyzed: {len(word_meanings)}")
    print(f"  Clean entries: {len(clean)}")
    print(f"  Conflicting entries: {len(conflicts)}")
    print(f"\nConflicts by type:")
    for ctype, items in by_type.items():
        print(f"  {ctype}: {len(items)}")
    
    print("\nCalculating coverage...")
    coverage = calculate_coverage(clean)
    print(f"  Clean coverage: {coverage.get('coverage', 0)}%")
    
    print("\nWorst offenders:")
    worst = analyze_worst_offenders(conflicts)
    for w in worst[:10]:
        print(f"  {w['word']}: {w['num_meanings']} meanings - {w['meanings'][:3]}...")
    
    results = {
        "total_entries": len(word_meanings),
        "conflicting_words": [c["voynich"] for c in conflicts],
        "conflict_count": len(conflicts),
        "clean_entries": len(clean),
        "removed_entries": [c["voynich"] for c in conflicts],
        "clean_coverage": f"{coverage.get('coverage', 0)}%",
        "conflicts_by_type": {k: len(v) for k, v in by_type.items()},
        "worst_offenders": worst,
        "full_conflicts": conflicts,
    }
    
    with open(DATA_DIR / "dictionary_conflicts.json", "w") as f:
        json.dump(results, f, indent=2)
    
    clean_dict = {
        "version": "clean_1.0",
        "description": "Dictionary with conflicting entries removed",
        "total_entries": len(clean),
        "entries": {e["voynich"]: e for e in clean},
    }
    
    with open(DATA_DIR / "clean_dictionary.json", "w") as f:
        json.dump(clean_dict, f, indent=2)
    
    report = generate_report(results, clean, conflicts, by_type, coverage)
    with open(DATA_DIR / "dictionary_conflicts_report.md", "w") as f:
        f.write(report)
    
    print(f"\n✅ Results saved to:")
    print(f"   - results/dictionary_conflicts.json")
    print(f"   - results/clean_dictionary.json")
    print(f"   - results/dictionary_conflicts_report.md")

def generate_report(results, clean, conflicts, by_type, coverage):
    lines = [
        "# Dictionary Conflict Analysis Report",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total entries analyzed | {results['total_entries']} |",
        f"| Clean entries | {results['clean_entries']} |",
        f"| Conflicting entries | {results['conflict_count']} |",
        f"| Conflict rate | {results['conflict_count']/results['total_entries']*100:.1f}% |",
        f"| Clean coverage | {coverage.get('coverage', 0)}% |",
        "",
        "## Conflicts by Type",
        "",
    ]
    
    for ctype, items in by_type.items():
        lines.append(f"### {ctype.replace('_', ' ').title()} ({len(items)} words)")
        lines.append("")
        
        if ctype == "cross_domain":
            lines.append("**These are SERIOUS conflicts** - same word means different things in unrelated domains.")
            lines.append("")
        elif ctype == "grammar_vs_content":
            lines.append("**Grammar vs content** - word acts as both grammar marker and content word.")
            lines.append("")
        elif ctype == "same_domain":
            lines.append("**Minor conflicts** - multiple related meanings within same domain.")
            lines.append("")
        
        for item in items[:10]:
            meanings = ", ".join(item["meanings"][:4])
            lines.append(f"- **{item['voynich']}**: {meanings}")
        
        if len(items) > 10:
            lines.append(f"- ... and {len(items)-10} more")
        lines.append("")
    
    lines.extend([
        "## Worst Offenders",
        "",
        "| Word | # Meanings | Examples | Type |",
        "|------|------------|----------|------|",
    ])
    
    for w in results["worst_offenders"][:15]:
        meanings = ", ".join(w["meanings"][:3])
        lines.append(f"| {w['word']} | {w['num_meanings']} | {meanings} | {w['conflict_type']} |")
    
    lines.extend([
        "",
        "## Critical Assessment",
        "",
        "### Red Flags Identified",
        "",
    ])
    
    cross_domain = by_type.get("cross_domain", [])
    if cross_domain:
        lines.append(f"1. **{len(cross_domain)} cross-domain conflicts**: Same words mean completely different things")
        example = cross_domain[0]
        lines.append(f"   - Example: `{example['voynich']}` = {', '.join(example['meanings'][:3])}")
        lines.append("")
    
    grammar_content = by_type.get("grammar_vs_content", [])
    if grammar_content:
        lines.append(f"2. **{len(grammar_content)} grammar/content conflicts**: Words serving dual purposes")
        lines.append("")
    
    conflict_rate = results['conflict_count']/results['total_entries']*100
    if conflict_rate > 30:
        lines.append(f"3. **High conflict rate ({conflict_rate:.1f}%)**: Over 30% of dictionary is ambiguous")
        lines.append("")
    
    lines.extend([
        "### Honest Assessment",
        "",
        f"- **Before cleaning**: ~{results['total_entries']} entries with potential overfitting",
        f"- **After cleaning**: {results['clean_entries']} reliable entries",
        f"- **Real coverage**: {coverage.get('coverage', 0)}%",
        f"- **Top 100 words in clean**: {coverage.get('top_100_words_matched', 'N/A')}",
        f"- **Top 100 coverage**: {coverage.get('top_100_coverage', 0)}%",
        "",
        "### Implications",
        "",
    ])
    
    clean_coverage = coverage.get('coverage', 0)
    if clean_coverage < 30:
        lines.append("⚠️ **Our claimed 50% translation rate is INFLATED**")
        lines.append("")
        lines.append("Many translations relied on ambiguous words that could mean multiple things.")
        lines.append("The true reliable coverage is significantly lower.")
    elif clean_coverage < 40:
        lines.append("⚠️ **Translation rate is partially inflated**")
        lines.append("")
        lines.append("Some translations are reliable, but many depend on context disambiguation.")
    else:
        lines.append("✅ **Core dictionary is relatively solid**")
        lines.append("")
        lines.append("Most entries have consistent meanings across sources.")
    
    lines.extend([
        "",
        "## Recommendations",
        "",
        "1. Use only entries from `clean_dictionary.json` for translation",
        "2. Cross-domain conflicts need manual review",
        "3. Re-run translation with clean dictionary to get honest metrics",
        "",
    ])
    
    return "\n".join(lines)

if __name__ == "__main__":
    main()
