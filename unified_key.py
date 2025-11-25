"""
Track 32: Unified Key Synthesis & Test
Combines zodiac and plant derivations with original key, then tests.
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ORIGINAL_KEY = {
    "o": "a", "k": "n", "y": "i", "t": "t", "e": "i", "l": "l", "m": "m",
    "a": "e", "i": "i", "d": "v", "c": "c", "q": "qu", "r": "?", "s": "x",
    "h": "r", "n": "n", "p": "p", "f": "f", "g": "g", "j": "j", "x": "x",
    "z": "z", "v": "v", "u": "u", "b": "b", "w": "w"
}

LATIN_WORDS = {
    "radix", "herba", "folium", "flos", "semen", "cortex", "succus",
    "oleum", "aqua", "bacca", "ramus", "fructus", "caulis", "stirps",
    "curat", "sanat", "valet", "prodest", "tollit", "solvit", "facit",
    "contra", "febris", "dolor", "ulcus", "tumor", "morbus",
    "calidus", "frigidus", "siccus", "humidus", "albus", "niger", "viridis",
    "aprilis", "martius", "maius", "iunius", "iulius", "augustus",
    "september", "october", "november", "december", "aries", "taurus",
    "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius",
    "capricornus", "aquarius", "pisces", "et", "in", "de", "ad", "cum",
    "pro", "per", "est", "sunt", "sit", "fiat", "ante", "post", "vel",
    "aut", "sed", "non", "que", "nam", "ita", "sic", "ut", "nec"
}


def load_json(path):
    with open(path) as f:
        return json.load(f)


def load_zodiac_derivation():
    try:
        data = load_json("results/zodiac_key_derivation.json")
        return data.get("derived_key", {}), data.get("character_derivations", [])
    except FileNotFoundError:
        return {}, []


def load_plant_derivation():
    try:
        data = load_json("results/plant_key_derivation.json")
        consistent = data.get("cross_check", {}).get("consistent_mappings", [])
        conflicts = data.get("cross_check", {}).get("conflicts", [])
        
        derived = {}
        for m in consistent:
            derived[m["voynich"]] = m["latin"]
        
        for c in conflicts:
            opts = c.get("latin_options", [])
            if opts:
                derived[c["voynich"]] = opts[0]
        
        return derived, data.get("derivation_attempts", [])
    except FileNotFoundError:
        return {}, []


def load_voynich_words():
    words = []
    try:
        with open("data/eva_ivtff.txt") as f:
            for line in f:
                if line.startswith("#") or not line.strip():
                    continue
                m = re.match(r'<([^>]+);H>\s*(.+)', line)
                if m:
                    text = m.group(2)
                    text_clean = re.sub(r'[!?<>@$\d]', '', text)
                    for w in re.split(r'[.\-=,\s]', text_clean):
                        if w and len(w) > 1:
                            words.append(w)
    except FileNotFoundError:
        pass
    return words


def decode_word(word, key):
    result = []
    for char in word:
        if char in key:
            result.append(key[char])
        else:
            result.append(char)
    return ''.join(result)


def is_latin_like(word):
    if len(word) < 2:
        return False
    vowels = set('aeiou')
    consonants = set('bcdfghjklmnpqrstvwxyz')
    
    has_vowel = any(c in vowels for c in word)
    has_consonant = any(c in consonants for c in word)
    
    if not has_vowel or not has_consonant:
        return False
    
    max_consec_cons = 0
    curr_cons = 0
    for c in word:
        if c in consonants:
            curr_cons += 1
            max_consec_cons = max(max_consec_cons, curr_cons)
        else:
            curr_cons = 0
    
    if max_consec_cons > 4:
        return False
    
    return True


def word_in_latin_vocab(word):
    word_lower = word.lower()
    if word_lower in LATIN_WORDS:
        return True
    for lw in LATIN_WORDS:
        if len(word_lower) >= 3 and (word_lower.startswith(lw[:3]) or lw.startswith(word_lower[:3])):
            return True
    return False


def merge_keys(zodiac_key, plant_key, original_key):
    all_chars = set(zodiac_key.keys()) | set(plant_key.keys()) | set(original_key.keys())
    
    merged = {}
    conflicts_resolved = []
    conflicts_unresolved = []
    
    for char in sorted(all_chars):
        z_val = zodiac_key.get(char)
        p_val = plant_key.get(char)
        o_val = original_key.get(char)
        
        sources = []
        if z_val:
            sources.append(("zodiac", z_val))
        if p_val:
            sources.append(("plant", p_val))
        if o_val:
            sources.append(("original", o_val))
        
        if not sources:
            continue
        
        values = [v for _, v in sources]
        value_counts = Counter(values)
        most_common = value_counts.most_common(1)[0]
        
        if len(set(values)) == 1:
            merged[char] = {
                "value": values[0],
                "confidence": 0.95,
                "sources": [s for s, _ in sources],
                "agreement": "full"
            }
        elif most_common[1] >= 2:
            merged[char] = {
                "value": most_common[0],
                "confidence": 0.7,
                "sources": [s for s, v in sources if v == most_common[0]],
                "agreement": "majority"
            }
            conflicts_resolved.append({
                "char": char,
                "chosen": most_common[0],
                "alternatives": {s: v for s, v in sources if v != most_common[0]},
                "reason": "majority vote"
            })
        else:
            merged[char] = {
                "value": o_val if o_val else values[0],
                "confidence": 0.3,
                "sources": ["original" if o_val else sources[0][0]],
                "agreement": "none"
            }
            conflicts_unresolved.append({
                "char": char,
                "options": {s: v for s, v in sources},
                "chosen": o_val if o_val else values[0],
                "reason": "defaulted to original"
            })
    
    return merged, conflicts_resolved, conflicts_unresolved


def build_simple_key(merged):
    return {char: info["value"] for char, info in merged.items()}


def test_key_on_corpus(key, words, label=""):
    decoded_words = []
    latin_like_count = 0
    vocab_match_count = 0
    
    sample_size = min(5000, len(words))
    test_words = words[:sample_size]
    
    for word in test_words:
        decoded = decode_word(word, key)
        decoded_words.append(decoded)
        
        if is_latin_like(decoded):
            latin_like_count += 1
        if word_in_latin_vocab(decoded):
            vocab_match_count += 1
    
    return {
        "label": label,
        "words_tested": sample_size,
        "latin_like_rate": latin_like_count / sample_size if sample_size else 0,
        "vocab_match_rate": vocab_match_count / sample_size if sample_size else 0,
        "sample_decodings": [(words[i], decoded_words[i]) for i in range(min(20, len(words)))]
    }


def test_zodiac_labels(key):
    try:
        data = load_json("results/zodiac_key_derivation.json")
        labels = data.get("labels_extracted", [])
    except FileNotFoundError:
        return {"match_rate": 0, "tested": 0}
    
    matches = 0
    total = 0
    
    month_names = {
        "martius", "aprilis", "maius", "iunius", "iulius", "augustus",
        "september", "october", "november", "december", "januarius", "februarius"
    }
    
    for folio_data in labels:
        expected_month = folio_data.get("expected_month", "").lower()
        for label in folio_data.get("labels", []):
            decoded = decode_word(label, key).lower()
            total += 1
            
            if decoded == expected_month:
                matches += 1
            elif any(decoded.startswith(m[:4]) for m in month_names):
                matches += 0.5
            elif is_latin_like(decoded):
                matches += 0.1
    
    return {
        "match_rate": matches / total if total else 0,
        "tested": total
    }


def test_plant_labels(key):
    try:
        data = load_json("results/plant_key_derivation.json")
        attempts = data.get("derivation_attempts", [])
    except FileNotFoundError:
        return {"match_rate": 0, "tested": 0}
    
    matches = 0
    total = 0
    
    for attempt in attempts:
        label_eva = attempt.get("label_eva", "")
        expected_latin = attempt.get("expected_latin", "").lower()
        
        if not label_eva or not expected_latin:
            continue
        
        decoded = decode_word(label_eva, key).lower()
        total += 1
        
        from difflib import SequenceMatcher
        ratio = SequenceMatcher(None, decoded, expected_latin).ratio()
        
        if ratio >= 0.8:
            matches += 1
        elif ratio >= 0.5:
            matches += 0.5
        elif is_latin_like(decoded):
            matches += 0.1
    
    return {
        "match_rate": matches / total if total else 0,
        "tested": total
    }


def calculate_coherence(key, words):
    sample = words[:1000]
    coherent = 0
    
    for word in sample:
        decoded = decode_word(word, key)
        if is_latin_like(decoded):
            coherent += 1
    
    return coherent / len(sample) if sample else 0


def compare_keys(original_results, unified_results):
    comparison = {
        "improvements": [],
        "regressions": [],
        "unchanged": []
    }
    
    metrics = ["latin_like_rate", "vocab_match_rate"]
    for metric in metrics:
        orig = original_results.get(metric, 0)
        unif = unified_results.get(metric, 0)
        
        diff = unif - orig
        entry = {"metric": metric, "original": orig, "unified": unif, "diff": diff}
        
        if diff > 0.01:
            comparison["improvements"].append(entry)
        elif diff < -0.01:
            comparison["regressions"].append(entry)
        else:
            comparison["unchanged"].append(entry)
    
    comparison["better_than_original"] = len(comparison["improvements"]) > len(comparison["regressions"])
    
    return comparison


def generate_report(results):
    lines = [
        "# Unified Key Synthesis Report",
        "",
        "## Summary",
        "",
        f"Combined derivations from zodiac ({len(results['zodiac_key'])} chars) "
        f"and plant ({len(results['plant_key'])} chars) analyses with original key.",
        "",
        "## Key Merge Statistics",
        "",
        f"- **Total characters mapped**: {len(results['unified_mappings'])}",
        f"- **Full agreement**: {sum(1 for v in results['unified_mappings'].values() if v['agreement'] == 'full')}",
        f"- **Majority agreement**: {sum(1 for v in results['unified_mappings'].values() if v['agreement'] == 'majority')}",
        f"- **No agreement**: {sum(1 for v in results['unified_mappings'].values() if v['agreement'] == 'none')}",
        f"- **Conflicts resolved**: {len(results['conflicts_resolved'])}",
        f"- **Conflicts unresolved**: {len(results['conflicts_unresolved'])}",
        "",
        "## Unified Key Table",
        "",
        "| Voynich | Unified | Confidence | Zodiac | Plant | Original | Agreement |",
        "|---------|---------|------------|--------|-------|----------|-----------|"
    ]
    
    for char in sorted(results['unified_mappings'].keys()):
        info = results['unified_mappings'][char]
        z = results['zodiac_key'].get(char, "-")
        p = results['plant_key'].get(char, "-")
        o = results['original_key'].get(char, "-")
        lines.append(f"| {char} | {info['value']} | {info['confidence']:.0%} | {z} | {p} | {o} | {info['agreement']} |")
    
    lines.extend([
        "",
        "## Conflict Resolutions",
        ""
    ])
    
    if results['conflicts_resolved']:
        for cr in results['conflicts_resolved']:
            lines.append(f"- **{cr['char']}**: Chose `{cr['chosen']}` (alternatives: {cr['alternatives']}) - {cr['reason']}")
    else:
        lines.append("No conflicts required resolution.")
    
    lines.extend([
        "",
        "## Test Results",
        "",
        "### Corpus Test",
        "",
        f"| Metric | Original Key | Unified Key | Change |",
        "|--------|--------------|-------------|--------|"
    ])
    
    tr = results['test_results']
    orig = results['original_test']
    
    lines.append(f"| Latin-like rate | {orig['latin_like_rate']:.1%} | {tr['corpus']['latin_like_rate']:.1%} | {(tr['corpus']['latin_like_rate'] - orig['latin_like_rate'])*100:+.1f}% |")
    lines.append(f"| Vocab match rate | {orig['vocab_match_rate']:.1%} | {tr['corpus']['vocab_match_rate']:.1%} | {(tr['corpus']['vocab_match_rate'] - orig['vocab_match_rate'])*100:+.1f}% |")
    
    lines.extend([
        "",
        "### Zodiac Labels",
        "",
        f"- Match rate: {tr['zodiac_match']:.1%}",
        f"- Labels tested: {results.get('zodiac_tested', 'N/A')}",
        "",
        "### Plant Labels", 
        "",
        f"- Match rate: {tr['plant_match']:.1%}",
        f"- Labels tested: {results.get('plant_tested', 'N/A')}",
        "",
        "### Coherence",
        "",
        f"- Original key coherence: {results['original_coherence']:.1%}",
        f"- Unified key coherence: {tr['coherence']:.1%}",
        "",
        "## Sample Decodings (Unified Key)",
        "",
        "| Voynich | Decoded |",
        "|---------|---------|"
    ])
    
    for voy, dec in tr['corpus']['sample_decodings'][:15]:
        lines.append(f"| {voy} | {dec} |")
    
    lines.extend([
        "",
        "## Comparison Summary",
        "",
        f"**Better than original**: {results['comparison']['better_than_original']}",
        ""
    ])
    
    if results['comparison']['improvements']:
        lines.append("### Improvements")
        for imp in results['comparison']['improvements']:
            lines.append(f"- {imp['metric']}: {imp['original']:.1%} → {imp['unified']:.1%} (+{imp['diff']*100:.1f}%)")
    
    if results['comparison']['regressions']:
        lines.append("")
        lines.append("### Regressions")
        for reg in results['comparison']['regressions']:
            lines.append(f"- {reg['metric']}: {reg['original']:.1%} → {reg['unified']:.1%} ({reg['diff']*100:.1f}%)")
    
    lines.extend([
        "",
        "## Verdict",
        ""
    ])
    
    comp = results['comparison']
    if comp['better_than_original'] and tr['coherence'] > results['original_coherence']:
        lines.append("✅ **ADOPT**: The unified key shows improvement over the original.")
        lines.append("")
        lines.append("The combined evidence from zodiac and plant derivations produces a more accurate key.")
    elif abs(tr['coherence'] - results['original_coherence']) < 0.05:
        lines.append("⚠️ **NEUTRAL**: The unified key performs similarly to the original.")
        lines.append("")
        lines.append("Neither key shows clear superiority. The encoding may not be simple substitution.")
    else:
        lines.append("❌ **REJECT**: The unified key performs worse than the original.")
        lines.append("")
        lines.append("This suggests the zodiac/plant derivations introduced errors, or the encoding is more complex.")
    
    lines.extend([
        "",
        "## Key Insights",
        "",
        "1. Characters with **full agreement** across all sources are most reliable",
        "2. Characters with **no agreement** indicate uncertain mappings or encoding complexity",
        "3. The overall low vocab match rate suggests the Voynich script is NOT a simple Latin substitution cipher",
        "",
        "---",
        "*Generated by unified_key.py - Track 32*"
    ])
    
    return '\n'.join(lines)


def main():
    print("Track 32: Unified Key Synthesis & Test")
    print("=" * 50)
    
    print("\n1. Loading derived keys...")
    zodiac_key, zodiac_derivations = load_zodiac_derivation()
    plant_key, plant_attempts = load_plant_derivation()
    
    print(f"   - Zodiac derivation: {len(zodiac_key)} characters")
    print(f"   - Plant derivation: {len(plant_key)} characters")
    print(f"   - Original key: {len(ORIGINAL_KEY)} characters")
    
    print("\n2. Merging keys...")
    merged, resolved, unresolved = merge_keys(zodiac_key, plant_key, ORIGINAL_KEY)
    print(f"   - Merged mappings: {len(merged)}")
    print(f"   - Conflicts resolved: {len(resolved)}")
    print(f"   - Conflicts unresolved: {len(unresolved)}")
    
    unified_simple = build_simple_key(merged)
    
    print("\n3. Loading corpus...")
    words = load_voynich_words()
    print(f"   - Words loaded: {len(words)}")
    
    print("\n4. Testing original key...")
    original_test = test_key_on_corpus(ORIGINAL_KEY, words, "original")
    original_coherence = calculate_coherence(ORIGINAL_KEY, words)
    print(f"   - Latin-like rate: {original_test['latin_like_rate']:.1%}")
    print(f"   - Vocab match rate: {original_test['vocab_match_rate']:.1%}")
    print(f"   - Coherence: {original_coherence:.1%}")
    
    print("\n5. Testing unified key...")
    unified_test = test_key_on_corpus(unified_simple, words, "unified")
    unified_coherence = calculate_coherence(unified_simple, words)
    print(f"   - Latin-like rate: {unified_test['latin_like_rate']:.1%}")
    print(f"   - Vocab match rate: {unified_test['vocab_match_rate']:.1%}")
    print(f"   - Coherence: {unified_coherence:.1%}")
    
    print("\n6. Testing on zodiac labels...")
    zodiac_test = test_zodiac_labels(unified_simple)
    print(f"   - Match rate: {zodiac_test['match_rate']:.1%}")
    print(f"   - Labels tested: {zodiac_test['tested']}")
    
    print("\n7. Testing on plant labels...")
    plant_test = test_plant_labels(unified_simple)
    print(f"   - Match rate: {plant_test['match_rate']:.1%}")
    print(f"   - Labels tested: {plant_test['tested']}")
    
    print("\n8. Comparing results...")
    comparison = compare_keys(original_test, unified_test)
    
    results = {
        "sources": ["zodiac", "plant", "original"],
        "zodiac_key": zodiac_key,
        "plant_key": plant_key,
        "original_key": ORIGINAL_KEY,
        "unified_mappings": merged,
        "unified_simple": unified_simple,
        "conflicts_resolved": resolved,
        "conflicts_unresolved": unresolved,
        "test_results": {
            "zodiac_match": zodiac_test['match_rate'],
            "plant_match": plant_test['match_rate'],
            "medieval_vocab": unified_test['vocab_match_rate'],
            "coherence": unified_coherence,
            "corpus": unified_test
        },
        "original_test": original_test,
        "original_coherence": original_coherence,
        "zodiac_tested": zodiac_test['tested'],
        "plant_tested": plant_test['tested'],
        "comparison": comparison
    }
    
    print("\n9. Saving results...")
    with open("results/unified_key.json", "w") as f:
        json.dump(results, f, indent=2)
    print("   - Saved results/unified_key.json")
    
    report = generate_report(results)
    with open("results/unified_key_report.md", "w") as f:
        f.write(report)
    print("   - Saved results/unified_key_report.md")
    
    print("\n" + "=" * 50)
    print("VERDICT:")
    if comparison['better_than_original'] and unified_coherence > original_coherence:
        print("✅ ADOPT: Unified key shows improvement")
    elif abs(unified_coherence - original_coherence) < 0.05:
        print("⚠️ NEUTRAL: Similar performance to original")
    else:
        print("❌ REJECT: Unified key performs worse")
    
    print("\nKey Statistics:")
    print(f"   Original → Latin-like: {original_test['latin_like_rate']:.1%}, Vocab: {original_test['vocab_match_rate']:.1%}")
    print(f"   Unified  → Latin-like: {unified_test['latin_like_rate']:.1%}, Vocab: {unified_test['vocab_match_rate']:.1%}")
    
    return results


if __name__ == "__main__":
    main()
